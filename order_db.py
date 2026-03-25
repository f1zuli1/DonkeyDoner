import sqlite3

conn   = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    card_number TEXT,
    items TEXT,
    total REAL
)
""")

conn.commit()
conn.close()

print("orders.db initialised successfully.")