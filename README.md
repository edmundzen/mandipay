# MandiPay

An AI selling agent for small farmers: photo → grade (A/B/C) → fair price → PayPal payment → dispute → farmer-approved refund.
Built for the PayPal AI Hackathon 2026. **PayPal Sandbox only — no real money.**

## Stack
Streamlit (Python) · Gemini API · PayPal Sandbox (Orders v2 + Refunds) · SQLite · Render

## Run locally
```bash
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Mac/Linux: cp .env.example .env  — then fill in your own keys
streamlit run app.py
```

## Files
| File | Owner | What |
|---|---|---|
| `app.py` | Nandini | Streamlit pages: sell, dispute, approve refunds, dashboard |
| `grading.py` | Nandini | Gemini grading + dispute referee |
| `db.py` | Nandini | SQLite orders |
| `prices.json` | Nandini | Base ₹/kg per crop (demo values) |
| `paypal.py` | Edmund | PayPal Sandbox: create, capture, refund |
| `test_paypal.py` | Edmund | One end-to-end Sandbox test |

## Rules
- Keys only in `.env` (local) and Render environment settings. Never in code, chat or screenshots.
- The AI only *suggests* refunds; the farmer always approves.

Team: Nandani Chauhan · Edmund Anthony
