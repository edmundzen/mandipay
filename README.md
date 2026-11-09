
# 🧺 MandiPay

An AI-powered quality grading and instant payment settlement system for agricultural produce.

---

## 🌟 What it does (5-Step Flow)

1. **Upload Produce Photo:** The farmer uploads an image of their produce (e.g., tomatoes) along with the quantity in kilograms.
2. **AI Quality Grading:** Gemini AI inspects the image, assigns a quality grade (**Grade A, B, or C**), detects defects, and explains the grading reasons.
3. **Fair Pricing & Payment Link:** MandiPay calculates a fair market price based on grade and quantity (in ₹ INR and Sandbox US$), generating a direct PayPal payment link.
4. **Instant Payment:** The buyer pays securely using PayPal Sandbox.
5. **AI Dispute Referee & Human Approval:** If the delivered produce quality is worse, the buyer uploads a photo. Gemini compares the before and after photos to suggest a fair refund percentage, which the farmer can approve with one click.

---

## 🚀 Live Demo & Repository

* **Live Web App:** [https://mandipay.onrender.com](https://mandipay.onrender.com) 
* **Repository:** Private / Public GitHub Repo
<img width="1920" height="1080" alt="Screenshot (1980)" src="https://github.com/user-attachments/assets/b292d6b0-04ee-4a2d-ba5c-7539621de91a" />
<img width="1920" height="1080" alt="Screenshot (1979)" src="https://github.com/user-attachments/assets/a48a7b4f-7fd6-486b-b0f1-d99773648fc9" />
---

## 🛠️ Tech Stack

* **Frontend & Web UI:** Streamlit
* **AI Model:** Google Gemini API (`gemini-2.5-flash` / `google-genai` SDK)
* **Payments:** PayPal REST API (Sandbox Mode)
* **Database:** SQLite3
* **Language:** Python 3.11+
* **Hosting:** Render

---

## Files
| File | Owner | What |
|---|---|---|
| `app.py` | Nandini | Streamlit pages: sell, dispute, approve refunds, dashboard |
| `grading.py` | Nandini | Gemini grading + dispute referee |
| `db.py` | Nandini | SQLite orders |
| `prices.json` | Nandini | Base ₹/kg per crop (demo values) |
| `paypal.py` | Edmund | PayPal Sandbox: create, capture, refund |
| `test_paypal.py` | Edmund | One end-to-end Sandbox test |

## 💻 How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.11+ installed.

### 2. Setup & Installation
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/mandipay.git](https://github.com/YOUR_USERNAME/mandipay.git)
cd mandipay

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows (Mac/Linux: source .venv/bin/activate)

# Install dependencies
pip install -r requirements.txt

## Rules
- Keys only in `.env` (local) and Render environment settings. Never in code, chat or screenshots.
- The AI only *suggests* refunds; the farmer always approves.


Team: Nandani Chauhan · Edmund Anthony
