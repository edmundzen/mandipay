import os, json, time, random
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Fallback list of valid model names
MODELS = ["gemini-3.8-flash", "gemini-2.5-flash"]

CFG = types.GenerateContentConfig(response_mime_type="application/json", temperature=0, tools=[])

GRADE_PROMPT = """You are a produce quality grader at an Indian mandi.
Grade the produce in the photo using this rubric:
A = uniform size, good colour, no spots or damage
B = minor marks, slight colour variation or uneven size
C = visible damage, rot, cracks or heavy spotting
Return JSON only:
{"crop": "tomato", "grade": "A", "reasons": ["..."], "defects": ["..."]}"""

JUDGE_PROMPT = """Photo 1 shows produce graded {grade} before sale.
Photo 2 shows what the buyer says they received.
Compare them. If quality is the same, refund_percent is 0.
If it is worse, suggest 10-100 depending on how bad. If spoiled or a different crop, 100.
Return JSON only:
{{"same_quality": true, "refund_percent": 0, "reason": "..."}}"""

def _img(data, mime):
    return types.Part.from_bytes(data=data, mime_type=mime or "image/jpeg")

class AIBusy(Exception):
    """Raised when every model attempt failed (overload, rate limit)."""

def _ask(contents):
    last = None
    for model in MODELS:
        for attempt in range(3):
            try:
                r = client.models.generate_content(model=model, contents=contents, config=CFG)
                return json.loads(r.text)
            except errors.APIError as e:
                # Include 404 so it moves to fallback if a model is deprecated/not found
                if getattr(e, "code", None) not in (404, 429, 500, 503):
                    raise
                last = e
                time.sleep(1.5 * 2 ** attempt + random.random())
    raise AIBusy("The AI grader is busy right now. Please wait a minute and try again.") from last

def grade(image_bytes, mime="image/jpeg"):
    return _ask([_img(image_bytes, mime), GRADE_PROMPT])

def judge(before_bytes, after_bytes, grade_letter, after_mime="image/jpeg"):
    return _ask([_img(before_bytes, "image/jpeg"), _img(after_bytes, after_mime),
                 JUDGE_PROMPT.format(grade=grade_letter)])
