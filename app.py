import os, json, uuid
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import grading, paypal, db

PRICES = json.load(open("prices.json"))
MULT = {"A": 1.0, "B": 0.8, "C": 0.55}
INR_PER_USD = 84            # demo rate; Sandbox charges in USD
os.makedirs("photos", exist_ok=True)

st.set_page_config(page_title="MandiPay", page_icon="🧺")
st.title("🧺 MandiPay")

# After paying, PayPal sends the buyer back here with ?token=ORDER_ID
token = st.query_params.get("token")
if token:
    o = db.by_paypal(token)
    if o and o["status"] == "created":
        cid = paypal.capture(token)
        db.update(o["id"], capture_id=cid, status="paid")
        st.success(f"Payment received for order #{o['id']}. Awaiting delivery.")
    st.query_params.clear()

def save_photo(data):
    path = f"photos/{uuid.uuid4().hex}.jpg"
    with open(path, "wb") as fh:
        fh.write(data)
    return path

page = st.sidebar.radio("Page", ["Farmer: sell", "Buyer: dispute",
                                 "Farmer: approve refunds", "Dashboard"])

# ------------------- 1. FARMER: SELL -------------------
if page == "Farmer: sell":
    f = st.file_uploader("Photo of your produce", type=["jpg", "jpeg", "png"])
    kg = st.number_input("Quantity (kg)", min_value=1.0, value=10.0)
    if f and st.button("Grade my produce"):
        with st.spinner("Grading..."):
            try:
                st.session_state.g = grading.grade(f.getvalue(), f.type)
                st.session_state.photo = f.getvalue()
            except grading.AIBusy as e:
                st.error(str(e))
    if "g" in st.session_state:
        g = st.session_state.g
        crop = g["crop"].lower()
        base = next((v for k, v in PRICES.items() if k in crop), 40)
        price_inr = round(base * MULT[g["grade"]] * kg)
        usd = round(price_inr / INR_PER_USD, 2)
        st.subheader(f"Grade {g['grade']} · {g['crop']}")
        st.write("Why: " + "; ".join(g["reasons"]))
        st.metric("Fair price", f"₹{price_inr}", f"≈ US${usd} (Sandbox)")
        if st.button("Create PayPal payment link"):
            oid = db.add(crop=g["crop"], kg=kg, grade=g["grade"],
                         reasons=json.dumps(g["reasons"]), price_inr=price_inr,
                         amount_usd=usd, photo=save_photo(st.session_state.photo))
            pid, link = paypal.create_order(usd, f"MP-{oid}")
            db.update(oid, paypal_order=pid)
            st.success(f"Order #{oid} created. Send this to the buyer:")
            st.link_button("Pay with PayPal", link)

# ------------------- 2. BUYER: DISPUTE -------------------
elif page == "Buyer: dispute":
    paid = [o for o in db.all_orders() if o["status"] == "paid"]
    if not paid:
        st.info("No paid orders yet.")
    else:
        o = st.selectbox("Your order", paid, format_func=lambda o:
                         f"#{o['id']} {o['crop']} {o['kg']} kg (grade {o['grade']})")
        f = st.file_uploader("Photo of what you received", type=["jpg", "jpeg", "png"])
        if f and st.button("Raise dispute"):
            with open(o["photo"], "rb") as fh:
                before = fh.read()
            with st.spinner("AI referee is comparing photos..."):
                try:
                    v = grading.judge(before, f.getvalue(), o["grade"], f.type)
                except grading.AIBusy as e:
                    st.error(str(e))
                    st.stop()
            db.update(o["id"], dispute_photo=save_photo(f.getvalue()),
                      status="refund_suggested",
                      refund_percent=v["refund_percent"], refund_reason=v["reason"])
            st.warning(f"AI suggests a {v['refund_percent']}% refund: {v['reason']}. "
                       "Waiting for the farmer to approve.")

# ------------------- 3. FARMER: APPROVE REFUNDS -------------------
elif page == "Farmer: approve refunds":
    pending = [o for o in db.all_orders() if o["status"] == "refund_suggested"]
    if not pending:
        st.info("No disputes waiting.")
    for o in pending:
        st.subheader(f"Order #{o['id']} · {o['crop']}")
        c1, c2 = st.columns(2)
        c1.image(o["photo"], caption="When graded")
        c2.image(o["dispute_photo"], caption="Buyer's photo")
        st.write(f"AI suggests **{o['refund_percent']}%**: {o['refund_reason']}")
        a, r = st.columns(2)
        if a.button("Approve refund", key=f"a{o['id']}"):
            pct = o["refund_percent"]
            if pct > 0:
                amount = None if pct >= 100 else round(o["amount_usd"] * pct / 100, 2)
                paypal.refund(o["capture_id"], amount)
            db.update(o["id"], status="refunded" if pct > 0 else "closed")
            st.rerun()
        if r.button("Reject", key=f"r{o['id']}"):
            db.update(o["id"], status="closed")
            st.rerun()

# ------------------- 4. DASHBOARD -------------------
elif page == "Dashboard":
    rows = [dict(o) for o in db.all_orders()]
    st.dataframe(rows, use_container_width=True)
