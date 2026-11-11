import os, json, time, random
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Fallback list of models (uses environment variable first if set)
PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MODELS = list(dict.fromkeys([PRIMARY_MODEL, "gemini-1.5-flash", "gemini-2.0-flash"]))

CFG = types.GenerateContentConfig(
    response_mime_type="application/json", 
    temperature=0, 
    tools=[]
)

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
    """Raised when every model attempt failed."""

def _ask(contents):
    last_err = None
    for model in MODELS:
        for attempt in range(2):
            try:
                r = client.models.generate_content(model=model, contents=contents, config=CFG)
                if r.text:
                    return json.loads(r.text)
            except Exception as e:
                # Catch ALL exceptions (404, 429, 503, connection drops) to try the next attempt/model
                last_err = e
                time.sleep(1 + random.random())
                
    raise AIBusy(f"AI Service Error: {last_err}") from last_err

def grade(image_bytes, mime="image/jpeg"):
    return _ask([_img(image_bytes, mime), GRADE_PROMPT])

def judge(before_bytes, after_bytes, grade_letter, after_mime="image/jpeg"):
    return _ask([_img(before_bytes, "image/jpeg"), _img(after_bytes, after_mime),
                 JUDGE_PROMPT.format(grade=grade_letter)])
