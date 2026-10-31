"""PayPal Sandbox helper for MandiPay (owner: Edmund).

Four functions the app calls; nothing else in the app talks to PayPal directly.
Sandbox only: BASE points at api-m.sandbox.paypal.com. Amounts are USD.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api-m.sandbox.paypal.com"
TIMEOUT = 30


def _token():
    r = requests.post(
        f"{BASE}/v1/oauth2/token",
        auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_SECRET"]),
        data={"grant_type": "client_credentials"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _headers():
    return {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}


def create_order(amount_usd, ref):
    """Create a PayPal order. Returns (paypal_order_id, approve_link)."""
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": ref,
            "amount": {"currency_code": "USD", "value": f"{amount_usd:.2f}"},
        }],
        "application_context": {
            "return_url": os.environ.get("APP_URL", "http://localhost:8501"),
            "cancel_url": os.environ.get("APP_URL", "http://localhost:8501"),
            "brand_name": "MandiPay",
            "user_action": "PAY_NOW",
        },
    }
    r = requests.post(f"{BASE}/v2/checkout/orders", json=body, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    o = r.json()
    approve = next(link["href"] for link in o["links"] if link["rel"] in ("approve", "payer-action"))
    return o["id"], approve


def capture(order_id):
    """Capture after the buyer approves. Returns capture_id (save it: refunds need it)."""
    r = requests.post(f"{BASE}/v2/checkout/orders/{order_id}/capture", headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["purchase_units"][0]["payments"]["captures"][0]["id"]


def refund(capture_id, amount_usd=None):
    """Refund a capture. amount_usd=None means a full refund. Returns PayPal's JSON."""
    body = {"amount": {"currency_code": "USD", "value": f"{amount_usd:.2f}"}} if amount_usd else {}
    r = requests.post(f"{BASE}/v2/payments/captures/{capture_id}/refund",
                      json=body, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
