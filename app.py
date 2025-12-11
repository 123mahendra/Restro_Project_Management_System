import mongo
from flask import Flask, Blueprint, render_template, request, redirect, make_response, get_flashed_messages, flash, \
    jsonify, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
import json
from db import create_user,get_database
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
from bson import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
import os
 

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your-secret-key"
CORS(app)

# Folder where dish images will be stored
app.config["UPLOAD_FOLDER"] = "static/assets/dishes"

# Create the folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

 

users = [
    {
        "id": "1",
        "first_name": "Admin",
        "last_name": "Admin",
        "email": "admin@admin.com",
        "password": "admin@admin",
        "role": "admin"
    }
]

sessions = {}

ANNOUNCEMENT_FILE = "static/data/announcements.json"

def load_announcements():
    with open(ANNOUNCEMENT_FILE, "r") as f:
        return json.load(f)

def save_announcements(data):
    with open(ANNOUNCEMENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Default home route

@app.route('/')
def home():
    user = None
    if "user_id" in session:
        user = {"first_name": session.get("user_first_name"),"last_name": session.get("user_last_name")}
    return render_template("index.html", user=user)

# Login Route

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/user/login', methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        db = get_database()
       
        user = db.users.find_one({"email": user_email})
        if not user:
            flash("Email not found!", "error")
            return redirect('/login')

        if not check_password_hash(user["password"], user_password):
            flash("Incorrect password!", "error")
            return redirect('/login')

        # Create session
        session["user_id"] = str(user["_id"])
        session["user_first_name"] = user["first_name"]
        session["user_last_name"] = user["last_name"]

        return redirect('/')

    return render_template("login.html")

# Logout Route

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect('/login')


# Register Route

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        user_email = request.form.get("email")
        contact_number = request.form.get("contact_number")

        db = get_database()

        # Check if email already exists
        existing_user = db.users.find_one({"email": user_email})
        if existing_user:
            flash("Email already registered!", "error")
            return redirect("/login")

        user_password = request.form.get("password")
        hashed_password = generate_password_hash(user_password)
        new_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_email,
            "password": hashed_password,
            "role":"customer",
            "contact_number":contact_number
        }
        create_user(new_user)
        flash("User register successfully!", "success")
        return redirect('/login')
        
# Admin Routes

@app.route('/admin')
def admin():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id in sessions:
        return redirect("/admin/dashboard")
    return render_template("admin/admin_login.html")


@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")

        for user in users:
            if (user_email == user["email"] 
                and user_password == user["password"] 
                and user['role'] == 'admin'):
                
                user_session_id = str(uuid.uuid4())
                sessions[user_session_id] = user
                
                resp = make_response(redirect("/admin/dashboard"))
                resp.set_cookie("user_session_id", user_session_id)
                return resp
            
        flash("Invalid email or password!", "error")
        return redirect("/admin")
    
    return render_template("admin/admin_login.html")


@app.route('/admin/dashboard')
def admin_dashboard():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id not in sessions:
        return redirect("/admin")

    user = sessions[user_session_id]
    return render_template("admin/admin_dashboard.html", user=user)


@app.route('/admin/logout')
def admin_logout():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id in sessions:
        sessions.pop(user_session_id)
        
    resp = make_response(redirect("/admin"))
    resp.set_cookie("user_session_id", '', expires=0, path='/')
    return resp

# Users

@app.route('/admin/users')
def admin_users():
    user_session_id = request.cookies.get("user_session_id")
    user = sessions[user_session_id]
    return render_template("admin/admin_dashboard.html",section="users",user=user)

@app.route('/api/users', methods=["GET"])
def user_list():
    db = get_database()
    users_collection = db.users
    users = list(users_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)

@app.route('/api/users/<user_id>', methods=["DELETE"])
def api_delete_user(user_id):
    db = get_database()
    users_collection = db.users

    result = users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 1:
        return jsonify({"success": True, "message": "User deleted"})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404
    
# Dishes

@app.route('/admin/dishes')
def admin_dishes():
    user_session_id = request.cookies.get("user_session_id")
    user = sessions.get(user_session_id)
    return render_template("admin/admin_dashboard.html", section="dishes", user=user)

@app.route('/api/dishes', methods=['POST'])
def add_dish():
    db = get_database()
    dishes = db.dishes

    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    image = request.files.get("image")

    if not name or not price:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    image_filename = None

    if image:
        filename = secure_filename(image.filename)
        print(filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        image_filename = filename

    dish_data = {
        "name": name,
        "price": float(price),
        "description": description,
        "image": image_filename,
        "created_at": datetime.utcnow()
    }

    result = dishes.insert_one(dish_data)

    return jsonify({
        "success": True,
        "message": "Dish added successfully",
        "id": str(result.inserted_id)
    })

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    db = get_database()
    dishes_collection = db.dishes

    dishes = list(dishes_collection.find({}))

    for d in dishes:
        d["_id"] = str(d["_id"])
        if "created_at" in d:
            d["created_at"] = str(d["created_at"])

    return jsonify(dishes)

@app.route('/api/dishes/<id>', methods=['DELETE'])
def delete_dish(id):
    db = get_database()
    dishes_collection = db.dishes

    dish = dishes_collection.find_one({"_id": ObjectId(id)})

    if not dish:
        return jsonify({"success": False, "error": "Dish not found"}), 404

    # delete image if exists
    if dish.get("image"):
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], dish["image"])
        if os.path.exists(img_path):
            os.remove(img_path)

    dishes_collection.delete_one({"_id": ObjectId(id)})

    return jsonify({"success": True, "message": "Dish deleted"})

@app.route('/api/dishes/<id>', methods=['GET'])
def get_single_dish(id):
    db = get_database()
    dishes = db.dishes

    dish = dishes.find_one({"_id": ObjectId(id)})
    if not dish:
        return jsonify({"error": "Dish not found"}), 404

    dish["_id"] = str(dish["_id"])
    return jsonify(dish)

@app.route('/api/dishes/<id>', methods=['PUT'])
def update_dish(id):
    db = get_database()
    dishes = db.dishes

    dish = dishes.find_one({"_id": ObjectId(id)})
    if not dish:
        return jsonify({"success": False, "error": "Dish not found"}), 404

    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    image = request.files.get("image")

    update_data = {
        "name": name,
        "price": float(price),
        "description": description
    }

    # If user uploads a new image
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        # delete old image
        if dish.get("image"):
            old_path = os.path.join(app.config["UPLOAD_FOLDER"], dish["image"])
            if os.path.exists(old_path):
                os.remove(old_path)

        update_data["image"] = filename

    dishes.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    return jsonify({"success": True, "message": "Dish updated"})

# Add dish to a day
@app.route('/admin/menu')
def admin_menu():
    user_session_id = request.cookies.get("user_session_id")
    user = sessions.get(user_session_id)
    return render_template("admin/admin_dashboard.html", section="menu", user=user)

@app.route("/api/menu", methods=["POST"])
def add_menu_dish():
    db = get_database()
    data = request.get_json()
    day = data["day"]
    dish_id = data["dishId"]

    dish = db.dishes.find_one({"_id": ObjectId(dish_id)})
    if not dish:
        return jsonify({"success": False, "message": "Dish not found"}), 404

    db.menu.insert_one({
        "day": day,
        "dish_id": ObjectId(dish_id)
    })
    return jsonify({"success": True})

# Get menu dishes for a day
@app.route("/api/menu/<day>", methods=["GET"])
def get_menu_day(day):
    db = get_database()
    entries = list(db.menu.find({"day": day.capitalize()}))
    for e in entries:
        dish = db.dishes.find_one({"_id": ObjectId(e["dish_id"])})
        e["_id"] = str(e["_id"])
        e["dish_id"] = str(e["dish_id"])
        e["dish_name"] = dish["name"]
        e["price"] = dish["price"]
        e["image"] = dish["image"]
        e["description"] = dish["description"]
    return jsonify(entries)

# Delete dish from day
@app.route("/api/menu/<id>", methods=["DELETE"])
def delete_menu_dish(id):
    db = get_database()
    db.menu.delete_one({"_id": ObjectId(id)})
    return jsonify({"success": True})



# Add item to cart
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    data = request.get_json()
    dish_id = data.get("dishId")
    quantity = int(data.get("quantity", 1))

    db = get_database()
    dish = db.dishes.find_one({"_id": ObjectId(dish_id)})
    if not dish:
        return jsonify({"success": False, "message": "Dish not found"}), 404

    # Initialize cart in session if not exists
    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    # Check if dish already in cart
    for item in cart:
        if item["dish_id"] == str(dish["_id"]):
            item["quantity"] += quantity
            session.modified = True
            return jsonify({"success": True, "message": "Cart updated"})

    # Add new dish to cart
    cart.append({
        "dish_id": str(dish["_id"]),
        "name": dish["name"],
        "price": dish["price"],
        "quantity": quantity
    })
    session.modified = True
    return jsonify({"success": True, "message": "Dish added to cart"})

# View cart
@app.route('/cart')
def view_cart():
    if "user_id" not in session:
        flash("Login required to view cart", "error")
        return redirect("/login")

    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/api/cart/count")
def cart_count():
    cart = session.get("cart", [])
    return jsonify({"count": sum(item["quantity"] for item in cart)})

# Update cart quantity
@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    data = request.get_json()
    dish_id = data.get("dishId")
    quantity = int(data.get("quantity", 1))

    cart = session.get("cart", [])
    for item in cart:
        if item["dish_id"] == dish_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item["quantity"] = quantity
            session.modified = True
            return jsonify({"success": True, "message": "Cart updated"})

    return jsonify({"success": False, "message": "Dish not in cart"}), 404

# Remove item from cart
@app.route('/api/cart/remove', methods=['POST'])
def remove_cart_item():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    data = request.get_json()
    dish_id = data.get("dishId")

    cart = session.get("cart", [])
    cart = [item for item in cart if item["dish_id"] != dish_id]
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True, "message": "Dish removed from cart"})

@app.route("/order")
def order():
    return render_template("order.html")
@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to checkout.")
        return redirect(url_for("login"))

    # Get database
    db = get_database()
    orders_col = db.orders

    # Get cart from session
    cart = session.get("cart", [])

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for("view_cart"))

    # Calculate total
    total = sum(float(item["price"]) * int(item["quantity"]) for item in cart)

    # Create order
    order_data = {
        "user_id": user_id,
        "items": cart,
        "total": total,
        "status": "pending",
        "created_at": datetime.now()
    }

    # Insert order into orders collection
    orders_col.insert_one(order_data)

    # Clear cart from session
    session["cart"] = []
    session.modified = True

    flash("Order placed successfully!")
    return redirect(url_for("home"))



@app.route("/order-success")
def order_success():
    return render_template("order_success.html")


@app.route('/admin/orders')
def admin_orders():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id not in sessions:
        return redirect("/admin")

    user = sessions[user_session_id]
    db = get_database()
    orders_collection = db.orders

    # Fetch all orders
    orders = list(orders_collection.find().sort("created_at", -1))  # latest first
    for order in orders:
        order["_id"] = str(order["_id"])
        # Check type before formatting
        if isinstance(order["created_at"], datetime):
            order["created_at"] = order["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            order["created_at"] = str(order["created_at"])

    return render_template("admin/admin_dashboard.html", section="orders", user=user, orders=orders)

@app.route("/admin/update-order-status", methods=["POST"])
def update_order_status():
    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("status")

    mongo.db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}}
    )

    return jsonify({"success": True})


@app.route("/menu")
def customer_menu():
    db = get_database()
    dishes = list(db.dishes.find({}))
    for d in dishes:
        d["_id"] = str(d["_id"])
    return render_template("menu.html", dishes=dishes)

# GET all announcements
@app.route("/api/announcements", methods=["GET"])
def get_announcements():
    return jsonify(load_announcements())


# ADD new announcement
@app.route("/api/announcements", methods=["POST"])
def create_announcement():
    data = request.get_json()
    announcements = load_announcements()

    new_id = str(uuid.uuid4())

    new_announcement = {
        "id": new_id,
        "title": data["title"],
        "message": data["message"],
        "type": data.get("type", "info"),
        "active": data.get("active", True)
    }

    announcements.append(new_announcement)
    save_announcements(announcements)

    return jsonify({"success": True, "announcement": new_announcement})


# UPDATE announcement
@app.route("/api/announcements/<id>", methods=["PUT"])
def update_announcement(id):
    data = request.get_json()
    announcements = load_announcements()

    for ann in announcements:
        if ann["id"] == id:
            ann.update(data)
            save_announcements(announcements)
            return jsonify({"success": True})

    return jsonify({"success": False, "msg": "Not found"}), 404


# DELETE
@app.route("/api/announcements/<id>", methods=["DELETE"])
def delete_announcement(id):
    announcements = load_announcements()
    announcements = [a for a in announcements if a["id"] != id]
    save_announcements(announcements)

    return jsonify({"success": True})


# Multilangual

def load_lang():
    with open("static/data/languages.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.context_processor
def inject_translations():
    lang = session.get("lang", "en")
    translations = load_lang()
    return dict(t=translations.get(lang, translations["en"]))

@app.route("/lang/<code>")
def switch_lang(code):
    if code in ["en", "fi"]:
        session["lang"] = code
    return redirect(request.referrer or "/")


if __name__ == "__main__":
    app.run(debug=True)
