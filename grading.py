import os, json
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CFG = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)

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

def grade(image_bytes, mime="image/jpeg"):
    r = client.models.generate_content(model=MODEL,
        contents=[_img(image_bytes, mime), GRADE_PROMPT], config=CFG)
    return json.loads(r.text)

def judge(before_bytes, after_bytes, grade_letter, after_mime="image/jpeg"):
    r = client.models.generate_content(model=MODEL,
        contents=[_img(before_bytes, "image/jpeg"), _img(after_bytes, after_mime),
                  JUDGE_PROMPT.format(grade=grade_letter)], config=CFG)
    return json.loads(r.text)

