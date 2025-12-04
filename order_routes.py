from flask import Blueprint, request, jsonify
from utils.auth import admin_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/admin/orders")
@admin_required
def orders_page():
    orders = list(db.orders.find())
    return render_template("admin_orders.html", orders=orders)
