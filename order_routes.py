from flask import Blueprint, render_template
from utils.auth import admin_required
from utils.db import db

order_bp = Blueprint("orders", __name__, url_prefix="/admin", template_folder="templates/admin")

@order_bp.route("/admin/orders")
@admin_required
def orders_page():
    orders = list(db.orders.find().sort("created_at", -1))
    for o in orders:
        o["_id_str"] = str(o["_id"])
    return render_template("admin_orders.html", orders=orders)
