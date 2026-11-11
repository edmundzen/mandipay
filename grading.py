"""AI grading for MandiPay.

Provider is chosen with AI_PROVIDER ("groq" or "gemini").
Default: groq if GROQ_API_KEY is set, otherwise gemini.
If the chosen provider fails, the other one is tried (when its key is set).
"""
import os, io, re, json, time, random, base64
from dotenv import load_dotenv
from PIL import Image
load_dotenv()

GRADE_PROMPT = """You are a produce quality grader at an Indian mandi.
Grade the produce in the photo using this rubric:
A = uniform size, good colour, no spots or damage
B = minor marks, slight colour variation or uneven size
C = visible damage, rot, cracks or heavy spotting
Return JSON only, no other text:
{"crop": "tomato", "grade": "A", "reasons": ["..."], "defects": ["..."]}"""

JUDGE_PROMPT = """Photo 1 shows produce graded {grade} before sale.
Photo 2 shows what the buyer says they received.
Compare them. If quality is the same, refund_percent is 0.
If it is worse, suggest 10-100 depending on how bad. If spoiled or a different crop, 100.
Return JSON only, no other text:
{{"same_quality": true, "refund_percent": 0, "reason": "..."}}"""


class AIBusy(Exception):
    """Raised when every provider/model attempt failed."""


def _shrink(data, max_side=1280):
    """Resize + re-encode as JPEG so phone photos stay under API size limits."""
    try:
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return data, "image/jpeg"


def _parse(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()  # drop reasoning
    try:
        return json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)      # tolerate ```json fences / extra words
        return json.loads(m.group(0))


# ---------------- Groq (Llama vision) ----------------
def _groq_ask(images, prompt):
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    models = list(dict.fromkeys([
        os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),           # Groq vision model (check console.groq.com/docs/vision)
        os.getenv("GROQ_FALLBACK_MODEL", os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")),
    ]))
    content = [{"type": "text", "text": prompt}]
    for data, mime in images:
        b64 = base64.b64encode(data).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
    last = None
    for model in models:
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model, temperature=0,
                    messages=[{"role": "user", "content": content}],
                    response_format={"type": "json_object"})
                return _parse(r.choices[0].message.content)
            except Exception as e:
                last = e
                time.sleep(1 + attempt + random.random())
    raise last


# ---------------- Gemini ----------------
def _gemini_ask(images, prompt):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    models = list(dict.fromkeys([os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                                 os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")]))
    contents = [types.Part.from_bytes(data=d, mime_type=m) for d, m in images] + [prompt]
    last = None
    for model in models:
        for attempt in range(2):
            try:
                r = client.models.generate_content(model=model, contents=contents, config=cfg)
                return _parse(r.text)
            except Exception as e:
                last = e
                time.sleep(1 + attempt + random.random())
    raise last


PROVIDERS = {"groq": ("GROQ_API_KEY", _groq_ask), "gemini": ("GEMINI_API_KEY", _gemini_ask)}


def _order():
    first = os.getenv("AI_PROVIDER", "groq" if os.getenv("GROQ_API_KEY") else "gemini").lower()
    order = [first] + [p for p in PROVIDERS if p != first]
    return [p for p in order if os.getenv(PROVIDERS[p][0])]


def _ask(images, prompt):
    images = [_shrink(d) for d, _ in images]
    errors = []
    for name in _order():
        try:
            return PROVIDERS[name][1](images, prompt)
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}: {str(e)[:150]}")
            print("[grading]", errors[-1])          # shows up in Render logs
    raise AIBusy("The AI grader is busy right now. Please wait a minute and try again.\n"
                 + " | ".join(errors))


def grade(image_bytes, mime="image/jpeg"):
    return _ask([(image_bytes, mime)], GRADE_PROMPT)


def judge(before_bytes, after_bytes, grade_letter, after_mime="image/jpeg"):
    return _ask([(before_bytes, "image/jpeg"), (after_bytes, after_mime)],
                JUDGE_PROMPT.format(grade=grade_letter))
