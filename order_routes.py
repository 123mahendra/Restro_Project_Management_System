from flask import Blueprint, redirect, session, render_template
from datetime import datetime
from bson import ObjectId
from utils.db import db

order_bp = Blueprint("order_bp", __name__)

# Place order
@order_bp.route("/order/place")
def place_order():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    cart = list(db.cart.find({"user_id": user_id}))
    if not cart:
        return "Cart is empty!"

    items = []
    total = 0

    for c in cart:
        item = db.menu_items.find_one({"_id": ObjectId(c["item_id"])})
        items.append({
            "item_id": str(item["_id"]),
            "name": item["name"],
            "price": item["price"],
            "quantity": c["quantity"]
        })
        total += item["price"] * c["quantity"]

    order = {
        "user_id": user_id,
        "items": items,
        "total_price": total,
        "status": "Pending",
        "created_at": datetime.utcnow()
    }

    order_id = db.orders.insert_one(order).inserted_id

    db.cart.delete_many({"user_id": user_id})

    return redirect(f"/order/{order_id}")


# Customer order tracking
@order_bp.route("/order/<order_id>")
def order_status(order_id):
    order = db.orders.find_one({"_id": ObjectId(order_id)})
    return render_template("order.html", order=order)
