from flask import Blueprint, session, request, jsonify
from bson import ObjectId
from utils.db import db
from utils.auth import login_required, current_user_id

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart", methods=["GET"])
@login_required
def get_cart():
    user_id = current_user_id()
    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    if not cart:
        return jsonify({"items": []})
    # populate product info
    for item in cart["items"]:
        product = db.menu.find_one({"_id": ObjectId(item["product_id"])})
        item["product"] = product
        item["product"]["_id"] = str(item["product"]["_id"])
    return jsonify(cart)


@cart_bp.route("/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    user_id = current_user_id()
    product_id = request.json.get("product_id")
    quantity = int(request.json.get("quantity", 1))

    cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    if not cart:
        cart = {"user_id": ObjectId(user_id), "items": [], "updated_at": datetime.datetime.utcnow()}

    # check if product exists in cart
    for item in cart["items"]:
        if str(item["product_id"]) == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append(
            {"product_id": ObjectId(product_id), "quantity": quantity, "added_at": datetime.datetime.utcnow()})

    db.carts.update_one({"user_id": ObjectId(user_id)}, {"$set": cart}, upsert=True)
    return jsonify({"ok": True})
