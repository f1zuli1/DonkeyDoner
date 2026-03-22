from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/orderpage')
def orderpage():
    return render_template('orderpage.html')

@app.route("/save-order", methods=["POST"])
def save_order():
    data = request.get_json()

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    # 1) INSERT
    cursor.execute("""
        INSERT INTO orders (name, phone, email, address, card_number, items, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(data.get("name", "")),
        str(data.get("phone", "")),
        str(data.get("email", "")),
        str(data.get("address", "")),
        hash(str(data.get("cardNumber", ""))),
        json.dumps(data.get("items", [])),
        float(data.get("total", 0))
    ))

    # 2) BURAYA YAZILIR 👇 (Sənin kod)
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    if count > 2:
        cursor.execute("""
            DELETE FROM orders 
            WHERE id IN (
                SELECT id FROM orders ORDER BY id ASC LIMIT 1
            )
        """)

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/get-orders")
def get_orders():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, email, address, items, total FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return jsonify(orders)

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

init_db()

@app.route("/get_user/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, phone, email, address FROM orders WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "name": user[0],
            "phone": user[1],
            "email": user[2],
            "address": user[3]
        })
    else:
        return jsonify({"error": "User not found"}), 404

def hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

if __name__ == '__main__':
    app.run(debug=True)
