"""One end-to-end Sandbox test: create -> buyer approves in browser -> capture -> partial refund.

Run:  python test_paypal.py
Log in on the approve page with your *Sandbox Personal* (buyer) account, not a real one.
"""
import paypal

print("1) Creating a US$5.00 order ...")
order_id, link = paypal.create_order(5.00, "MP-TEST-1")
print("   order id:", order_id)
print("2) Open this link, log in as the Sandbox buyer and approve:\n  ", link)
input("   Press Enter here after approving (you can ignore the localhost page it returns to) ... ")

print("3) Capturing ...")
cap = paypal.capture(order_id)
print("   capture id:", cap)

print("4) Refunding US$1.50 (partial) ...")
res = paypal.refund(cap, 1.50)
print("   refund status:", res.get("status"), "| refund id:", res.get("id"))
print("\nAll good: create, capture and refund work. Push paypal.py and tell Nandini.")
