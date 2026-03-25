from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib
import json

app = Flask(__name__)

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


@app.route("/")
def index():
    return render_template("register.html")

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/order")
def order():
    return render_template("order.html")

@app.route("/orderpage")
def orderpage():
    return render_template("orderpage.html")

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/giftorderpage")
def giftorderpage():
    return render_template("giftorderpage.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signin")
def signin_page():
    return render_template("signin.html")


@app.route("/register", methods=["POST"])
def register_user():
    #copilot 48, 49, 50
    data = request.get_json()
    if not data:
        data = {}

    name = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    try:
        conn.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (name, email, password))
        conn.commit()
        #copliot
        row = conn.execute("SELECT id, username FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        #copilot
        return jsonify({"message": "ok", "user_id": row[0], "username": row[1]})
    except:
        conn.close()
        #copilot
        return jsonify({"message": "email_exists"}), 409


@app.route("/signin", methods=["POST"])
def login():
    #copilot 74,75,76
    data = request.get_json()
    if not data:
        data = {}

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    row = conn.execute("SELECT id, username FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()

    if row:
        return jsonify({"status": "ok", "user_id": row[0], "username": row[1]})
    else:
        return jsonify({"status": "fail"})


@app.route("/save-order", methods=["POST"])
def save_order():
    #copilot 94,95,96
    data = request.get_json()
    if not data:
        data = {}

    user_id = str(data.get("user_id", ""))
    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    address = data.get("address", "")
    card = hash_text(str(data.get("cardNumber", "")))
    items = json.dumps(data.get("items", []))
    total = float(data.get("total", 0))

    conn = sqlite3.connect("orders.db")
    conn.execute("INSERT INTO orders (user_id,name,phone,email,address,card_number,items,total) VALUES (?,?,?,?,?,?,?,?)",
                 (user_id, name, phone, email, address, card, items, total))
    conn.execute("DELETE FROM orders WHERE user_id=? AND id NOT IN (SELECT id FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10)",
                 (user_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# DUZELTME: <int:user_id> deyil, <user_id> -- cunki DB-de TEXT kimi saxlanilir
@app.route("/get-orders/<user_id>")
def get_orders(user_id):
    conn = sqlite3.connect("orders.db")
    rows = conn.execute("SELECT items, total FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()

    result = []
    #copilot for r in rows: 
    for r in rows:
        try:
            items = json.loads(r[0])
        except:
            items = []
        result.append([items, r[1]])

    return jsonify(result)


@app.route("/delete-order", methods=["POST"])
def delete_order():
    #copilot 140,141,142
    data = request.get_json()
    if not data:
        data = {}

    user_id = str(data.get("user_id", ""))
    index = data.get("index")

    conn = sqlite3.connect("orders.db")
    rows = conn.execute("SELECT id FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()

    #copilot
    if rows and index >= 0 and index < len(rows):
        order_id = rows[index][0]
        conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()

    conn.close()
    #copilot
    return jsonify({"status": "ok"})


@app.route("/delete-all-orders", methods=["POST"])
def delete_all_orders():
    #copilot 164,165,166
    data = request.get_json()
    if not data:
        data = {}

    user_id = str(data.get("user_id", ""))

    conn = sqlite3.connect("orders.db")
    if user_id:
        conn.execute("DELETE FROM orders WHERE user_id=?", (user_id,))
    else:
        conn.execute("DELETE FROM orders")
    conn.commit()
    conn.close()

    #copilot
    return jsonify({"status": "ok"})


@app.route("/my-orders/<int:user_id>")
def my_orders(user_id):
    conn = sqlite3.connect("orders.db")
    rows = conn.execute("SELECT name,phone,address,items,total FROM orders WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    #copilot
    return jsonify(rows)


@app.route("/get_user/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect("orders.db")
    row = conn.execute("SELECT name,phone,email,address FROM orders WHERE id=?", (user_id,)).fetchone()
    conn.close()

    #copliot
    if row:
        return jsonify({"name": row[0], "phone": row[1], "email": row[2], "address": row[3]})
    return jsonify({"error": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)