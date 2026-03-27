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

@app.route("/register", methods = ["GET"])
def register():
    return render_template("register.html")

@app.route("/signin")
def signin_page():
    return render_template("signin.html")
#__________________________________________
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
#________________________________________________

conn   = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    phone TEXT NOT NULL
)
""")

conn.commit()
conn.close()
#_______________________________________________

#yeni istifadeci
@app.route("/register", methods=["POST"])
def register_user():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    name = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone", "")

    conn = sqlite3.connect("users.db")
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, phone) VALUES (?,?,?,?)",
            (name, email, password, phone)
        )
        conn.commit()                                                                              #copilot fetchone
        row = conn.execute("SELECT id, username, email, phone FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        #copilot jsonify
        return jsonify({
            "message": "ok",
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "phone": row[3]
        })
    #copilot Exception yazdi
    except Exception as e:
        conn.close()

#giris
@app.route("/signin", methods=["POST"])
def login():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    row = conn.execute(
        "SELECT id, username, email, phone FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()#copilot fetchone
    conn.close()

    if row:
        return jsonify({
            "status": "ok",
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "phone": row[3]
        })
    #copilot else
    else:
        return jsonify({"status": "fail"})

#hesab sil
@app.route("/delete-account", methods=["POST"])
def delete_account():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    user_id = str(data.get("user_id", ""))
    password = data.get("password", "")

    #copilot if not user_id or not password
    if not user_id or not password:
        return jsonify({"status": "fail", "message": "user_id and password required"})

    conn = sqlite3.connect("users.db")
    
    user = conn.execute(
        "SELECT id FROM users WHERE id=? AND password=?",
        (user_id, password)
    ).fetchone()

    if not user:
        conn.close()
        #copilot return jsonify
        return jsonify({"status": "fail", "message": "Invalid password"})

    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    orders_conn = sqlite3.connect("orders.db")
    orders_conn.execute("DELETE FROM orders WHERE user_id=?", (user_id,))
    orders_conn.commit()
    orders_conn.close()

    #copilot return jsonify
    return jsonify({"status": "ok", "message": "Account deleted successfully"})

#profil melumatlarini yenile
@app.route("/update-profile", methods=["POST"])
def update_profile():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    user_id = str(data.get("user_id", ""))
    username = data.get("username", "")
    phone = data.get("phone", "")
    email = data.get("email", "")

    #copilot if not user_id
    if not user_id:
        return jsonify({"status": "fail", "message": "user_id required"})

    conn = sqlite3.connect("users.db")
    try:
        conn.execute(
            "UPDATE users SET username=?, phone=?, email=? WHERE id=?",
            (username, phone, email, user_id)
        )
        conn.commit()
        conn.close()
        #copilot return jsonify
        return jsonify({"status": "ok", "message": "Profile updated"})
    #copilot exception
    except Exception as e:
        conn.close()
        return jsonify({"status": "fail", "message": str(e)})

#sifarisleri yadda saxla
@app.route("/save-order", methods=["POST"])
def save_order():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
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
    conn.execute(
        "INSERT INTO orders (user_id,name,phone,email,address,card_number,items,total) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, name, phone, email, address, card, items, total)
    )

    conn.execute(
        "DELETE FROM orders WHERE user_id=? AND id NOT IN (SELECT id FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10)",
        (user_id, user_id)
    )
    conn.commit()
    conn.close()

    #copilot
    return jsonify({"status": "ok"})

#user_id nin history sini qaytarir
@app.route("/get-orders/<user_id>")
def get_orders(user_id):
    conn = sqlite3.connect("orders.db")
    rows = conn.execute(
        "SELECT items, total, id FROM orders WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()#copilot fetchall
    conn.close()

    #copilot result = [] and for r in rows:
    result = []
    for r in rows:
        try:
            items = json.loads(r[0])
        except:
            items = []
        result.append([items, r[1], r[2]])

    return jsonify(result)

#secilen sifarisi silir
@app.route("/delete-order", methods=["POST"])
def delete_order():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    user_id = str(data.get("user_id", ""))
    index = data.get("index")

    conn = sqlite3.connect("orders.db")
    rows = conn.execute(
        "SELECT id FROM orders WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()#copilot fetchall

    if rows and index >= 0 and index < len(rows):
        order_id = rows[index][0]
        conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()

    conn.close()
    #copilot return jsonify
    return jsonify({"status": "ok"})

#butun sifarisleri silir
@app.route("/delete-all-orders", methods=["POST"])
def delete_all_orders():
    #copilot
    data = request.get_json()
    #copilot
    if not data:
        #copilot
        data = {}

    user_id = str(data.get("user_id", ""))

    conn = sqlite3.connect("orders.db")
    if user_id:
        conn.execute("DELETE FROM orders WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    #copilot
    return jsonify({"status": "ok"})

#her istifadecinin ozune aid history paneli
@app.route("/my-orders/<int:user_id>")
def my_orders(user_id):
    conn = sqlite3.connect("orders.db")
    rows = conn.execute(
        "SELECT name, phone, address, items, total FROM orders WHERE user_id=?",(user_id,)).fetchall()#copilot fetchall
    conn.close()
    return jsonify(rows)

#istifadecinin eger profili varsa orderpage.html de olan inputlari doldurur
@app.route("/get_user/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect("orders.db")
    row = conn.execute(
        "SELECT name, phone, email, address FROM orders WHERE id=?",
        (user_id,)
    ).fetchone() #copilot fetchone
    conn.close()

    if row:
        return jsonify({
            "name": row[0],
            "phone": row[1],
            "email": row[2],
            "address": row[3]
        })
    #copilot
    else:
        return jsonify({"error": "User not found"})

if __name__ == "__main__":
    app.run(debug=True)