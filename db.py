import sqlite3
CON = sqlite3.connect("mandipay.db", check_same_thread=False)
CON.row_factory = sqlite3.Row
CON.execute("""CREATE TABLE IF NOT EXISTS orders(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  crop TEXT, kg REAL, grade TEXT, reasons TEXT,
  price_inr REAL, amount_usd REAL, photo TEXT,
  paypal_order TEXT, capture_id TEXT, status TEXT DEFAULT 'created',
  dispute_photo TEXT, refund_percent INTEGER, refund_reason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
CON.commit()

def add(**f):
    cols, marks = ",".join(f), ",".join("?" * len(f))
    cur = CON.execute(f"INSERT INTO orders({cols}) VALUES({marks})", tuple(f.values()))
    CON.commit()
    return cur.lastrowid

def update(oid, **f):
    sets = ",".join(f"{k}=?" for k in f)
    CON.execute(f"UPDATE orders SET {sets} WHERE id=?", (*f.values(), oid))
    CON.commit()

def by_paypal(pid):
    row = CON.execute("SELECT * FROM orders WHERE paypal_order=?", (pid,)).fetchone()
    return dict(row) if row else None

def all_orders():
    return [dict(r) for r in CON.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()]
