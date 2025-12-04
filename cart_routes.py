import datetime
from flask import Blueprint, session, request, jsonify
from bson import ObjectId
from utils.db import db  # MongoDB connection
from utils.auth import login_required  # decorator to check logged-in customer

cart_bp = Blueprint("cart", __name__)

# Helper: Get current user's cart
def get_cart():
    customer_id = session.get("customer_id")
    if not customer_id:
        return []
    cart_doc = db.carts.find_one({"customer_id": customer_id})
    return cart_doc["items"] if cart_doc else []

# Helper: Save cart to DB
def save_cart(items):
    customer_id = session.get("customer_id")
    if not customer_id:
        return
    db.carts.update_one(
        {"customer_id": customer_id},
        {"$set": {"items": items, "updated_at": datetime.datetime.utcnow()}},
        upsert=True
    )

# Get cart items
@cart_bp.route("/api/cart", methods=["GET"])
@login_required
def api_get_cart():
    return jsonify(get_cart())

# Add item to cart
@cart_bp.route("/api/cart/add", methods=["POST"])
@login_required
def api_add_cart():
    data = request.json or {}
    item_id = data.get("item_id")
    qty = int(data.get("qty", 1))
    if not item_id:
        return jsonify({"error": "item_id required"}), 400

    menu_item = db.menu.find_one({"_id": ObjectId(item_id)})
    if not menu_item:
        return jsonify({"error": "Menu item not found"}), 404

    cart_items = get_cart()
    # Check if item exists
    for it in cart_items:
        if it["item_id"] == item_id:
            it["qty"] += qty
            break
    else:
        cart_items.append({
            "item_id": item_id,
            "name": menu_item["name_en"],
            "price": menu_item["price"],
            "qty": qty
        })

    save_cart(cart_items)
    return jsonify(cart_items)

# Remove item from cart
@cart_bp.route("/api/cart/remove", methods=["POST"])
@login_required
def api_remove_cart():
    data = request.json or {}
    item_id = data.get("item_id")
    cart_items = get_cart()
    cart_items = [it for it in cart_items if it["item_id"] != item_id]
    save_cart(cart_items)
    return jsonify(cart_items)

# Checkout
@cart_bp.route("/api/cart/checkout", methods=["POST"])
@login_required
def api_checkout_cart():
    data = request.json or {}
    phone = data.get("phone")
    pickup_time = data.get("pickup_time")
    customer_id = session.get("customer_id")
    customer_name = session.get("customer_name")

    if not phone or not pickup_time:
        return jsonify({"error": "phone and pickup_time required"}), 400

    cart_items = get_cart()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total = sum(it["price"] * it["qty"] for it in cart_items)

    order_doc = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "items": cart_items,
        "total": total,
        "phone": phone,
        "pickup_time": pickup_time,
        "status": "Pending",
        "created_at": datetime.datetime.utcnow()
    }

    db.orders.insert_one(order_doc)

    # Clear cart after checkout
    save_cart([])
    return jsonify({"ok": True})
