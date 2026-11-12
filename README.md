# 🧺 MandiPay

AI quality grading + PayPal payments and refunds for small farmers selling produce.

> ⚠️ **Sandbox only.** All payments use the PayPal Developer Sandbox. No real money moves.

---

## 🌟 What it does (5 steps)

1. **Upload a produce photo.** The farmer uploads a photo (e.g. tomatoes) and the quantity in kg.
2. **AI quality grading.** A vision AI model grades the produce **A / B / C**, lists defects and explains why.
3. **Fair price + PayPal link.** MandiPay prices the lot from the grade and quantity (₹ INR, shown with a Sandbox US$ amount) and creates a PayPal payment link.
4. **Buyer pays with PayPal.** The buyer approves the payment in PayPal checkout and MandiPay captures it.
5. **AI dispute referee + human approval.** If the delivery is worse than promised, the buyer uploads a photo. The AI compares the "before" and "after" photos and suggests a refund %. **The farmer approves or rejects**, and only then does MandiPay call PayPal to refund.

---

## 🚀 Live demo & repo

* **Live app:** https://mandipay-sg.onrender.com (free hosting, so the first load can take ~50 s)
* **Repository:** https://github.com/edmundzen/mandipay

<img width="1920" height="1080" alt="Screenshot (1980)" src="https://github.com/user-attachments/assets/b292d6b0-04ee-4a2d-ba5c-7539621de91a" />
<img width="1920" height="1080" alt="Screenshot (1979)" src="https://github.com/user-attachments/assets/a48a7b4f-7fd6-486b-b0f1-d99773648fc9" />

---

## 💳 How we use PayPal

* **Orders API v2:** `POST /v2/checkout/orders` creates an order for the graded price. The buyer approves in PayPal checkout and is sent back to the app (`APP_URL`), where we call `POST /v2/checkout/orders/{id}/capture`.
* **Safe capture:** every capture sends a `PayPal-Request-Id` header, so a page reload can't charge twice. If PayPal answers `422` (already captured), we look up the order and reuse the existing capture.
* **Refunds API:** `POST /v2/payments/captures/{id}/refund` sends a **full or partial** refund, matching the refund % the farmer approved.
* Code: [`paypal.py`](paypal.py)

## 🤖 How we use AI

* **Grading:** a vision model returns structured JSON: `grade`, `crop`, `reasons`, `defects`.
* **Dispute referee:** the same model compares the original and delivered photos and returns `refund_percent` and `reason`.
* **Providers:** **Groq** (`qwen/qwen3.8-27b` vision model) is primary, with **Google Gemini** (`gemini-2.5-flash`) as an automatic backup if Groq is busy or rate-limited. Temperature 0 and JSON output keep results consistent.
* **Human in the loop:** the AI only *suggests* a refund. A person always approves before any money moves.
* Code: [`grading.py`](grading.py)

## ☁️ How we use Render

The Streamlit app runs as a Render **Web Service** (free tier), deployed from this GitHub repo.
* Build: `pip install -r requirements.txt`
* Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
* Keys are stored as Render **environment variables**, never in the repo.

---

## 🛠️ Tech stack

| Part | Tool |
|---|---|
| UI | Streamlit (Python) |
| AI | Groq (Qwen vision), Google Gemini backup |
| Payments | PayPal Orders API v2 + Refunds API (Sandbox) |
| Database | SQLite |
| Hosting | Render |

## 📁 Files

| File | Owner | What |
|---|---|---|
| `app.py` | Nandini | Streamlit pages: sell, dispute, approve refunds, dashboard |
| `grading.py` | Nandini | AI grading + dispute referee (Groq, Gemini backup) |
| `db.py` | Nandini | SQLite orders |
| `prices.json` | Nandini | Base ₹/kg per crop (demo values) |
| `paypal.py` | Edmund | PayPal Sandbox: create, capture, refund |
| `test_paypal.py` | Edmund | End-to-end Sandbox test |
| `Test_photos/` | Both | Sample photos: T6–T10 fresh, T11–T15 wrinkled, T1–T5 rotten |

---

## 💻 Run locally

Needs Python 3.11+.

```bash
git clone https://github.com/edmundzen/mandipay.git
cd mandipay
python -m venv .venv
.venv\Scripts\activate          # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

Create a `.env` file (never commit it):

```
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_SECRET=your_sandbox_secret
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key      # optional backup
AI_PROVIDER=groq
APP_URL=http://localhost:8501
```

Run:

```bash
streamlit run app.py
```

## 🧪 Try it

1. **Farmer: sell** → upload `Test_photos/T8.jpg`, 10 kg → **Grade** → **Create PayPal payment link**.
2. Pay with a PayPal **Sandbox personal (buyer)** account.
3. **Buyer: dispute** → pick the order → upload `Test_photos/T1.jpg` → **Raise dispute**.
4. **Farmer: approve refunds** → **Approve refund**.
5. **Dashboard** → status shows **refunded**.

## 📏 Rules

- Keys only in `.env` (local) and Render environment settings. Never in code, chat or screenshots.
- The AI only *suggests* refunds; the farmer always approves.
- Sandbox only.

---

Team: Nandani Chauhan · Edmund Anthony · MIT License
