import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
import stripe

load_dotenv()

# Config
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/restaurant_db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

CORS(app, supports_credentials=True)
jwt = JWTManager(app)

# Mongo
client = MongoClient(MONGODB_URI)
db = client.get_default_database()
users_col = db["users"]
orders_col = db["orders"]

# Stripe init
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# ----------------------
# Utilities
# ----------------------
def serialize_doc(doc):
    if not doc: return None
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    # convert ObjectId fields (owner_id)
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

def is_admin_claims():
    claims = get_jwt()
    return claims.get("role") == "admin"

# ----------------------
# Auth: register / login
# ----------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400
    if users_col.find_one({"username": username}):
        return jsonify({"msg": "username exists"}), 409
    user = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "role": data.get("role", "user")  # default role=user; admin can be set manually in DB
    }
    res = users_col.insert_one(user)
    user_out = {"id": str(res.inserted_id), "username": username, "role": user["role"]}
    return jsonify({"user": user_out}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = users_col.find_one({"username": username})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"msg": "Bad credentials"}), 401
    additional_claims = {"role": user.get("role", "user")}
    access_token = create_access_token(identity=str(user["_id"]), additional_claims=additional_claims)
    user_out = {"id": str(user["_id"]), "username": user["username"], "role": user.get("role", "user")}
    return jsonify({"access_token": access_token, "user": user_out})

# ----------------------
# Orders
# ----------------------
@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json or {}
    # minimal validation
    required = ["name", "number", "order", "quantity"]
    for r in required:
        if not data.get(r):
            return jsonify({"msg": f"{r} is required"}), 400

    order_doc = {
        "name": data.get("name"),
        "number": data.get("number"),
        "items": data.get("items", []),   # cart items list [{name,price,qty}]
        "order": data.get("order", ""),   # free-text order name if used
        "extra": data.get("extra", ""),
        "quantity": int(data.get("quantity", 1)),
        "datetime": data.get("datetime", ""),
        "address": data.get("address", ""),
        "message": data.get("message", ""),
        "total": float(data.get("total", 0)),
        "status": "pending",
    }
    res = orders_col.insert_one(order_doc)
    return jsonify({"msg": "order saved", "order_id": str(res.inserted_id)}), 201

@app.route("/api/orders", methods=["GET"])
@jwt_required()
def list_user_orders():
    # lists orders for logged-in user (if we had owner field). For now return all for admin; users get only theirs if owner set.
    identity = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") == "admin":
        docs = list(orders_col.find().sort("_id", -1))
    else:
        # If orders had owner_id we would filter: orders_col.find({"owner_id": ObjectId(identity)})
        docs = list(orders_col.find({"number": {"$exists": True}}).sort("_id", -1))  # basic
    return jsonify([serialize_doc(d) for d in docs]), 200

# Admin-only endpoint (explicit)
@app.route("/api/admin/orders", methods=["GET"])
@jwt_required()
def admin_get_orders():
    if not is_admin_claims():
        return jsonify({"msg": "admin required"}), 403
    docs = list(orders_col.find().sort("_id", -1))
    return jsonify([serialize_doc(d) for d in docs]), 200

# Update order status (admin)
@app.route("/api/admin/orders/<order_id>/status", methods=["PUT"])
@jwt_required()
def admin_update_status(order_id):
    if not is_admin_claims():
        return jsonify({"msg": "admin required"}), 403
    new_status = (request.json or {}).get("status")
    if not new_status:
        return jsonify({"msg": "status required"}), 400
    try:
        oid = ObjectId(order_id)
    except Exception:
        return jsonify({"msg": "invalid id"}), 400
    orders_col.update_one({"_id": oid}, {"$set": {"status": new_status}})
    doc = orders_col.find_one({"_id": oid})
    return jsonify(serialize_doc(doc)), 200

# ----------------------
# Stripe Checkout session
# ----------------------
@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if not STRIPE_SECRET_KEY:
        return jsonify({"msg": "stripe not configured"}), 500
    data = request.json or {}
    items = data.get("items", [])  # expected [{name, price, quantity}]
    if not items:
        return jsonify({"msg": "no items"}), 400

    line_items = []
    for it in items:
        # Stripe expects amounts in cents (integer)
        price_cents = int(float(it.get("price", 0)) * 100)
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": it.get("name")},
                "unit_amount": price_cents,
            },
            "quantity": int(it.get("quantity", 1))
        })

    # create session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url=data.get("success_url") or "http://localhost:5000/payment-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=data.get("cancel_url") or "http://localhost:5000/payment-cancel",
        )
        return jsonify({"id": session.id, "url": session.url})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# ----------------------
# Simple route to serve index
# ----------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_index(path):
    # Serve index.html for frontend routes
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
