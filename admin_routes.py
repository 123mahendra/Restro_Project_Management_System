from flask import Blueprint, render_template, request, redirect, url_for
from bson import ObjectId
from utils.auth import admin_required, is_admin_session
from utils.db import db

admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/admin")
@admin_required
def dashboard_root():
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    menu_items = list(db.menu.find().sort([("category",1),("name_en",1)]))
    orders = list(db.orders.find().sort("created_at",-1))

    # convert _id to string
    for m in menu_items: m["_id"] = str(m["_id"])
    for o in orders: o["_id_str"] = str(o["_id"])

    return render_template("admin_dashboard.html", menu=menu_items, orders=orders)


@admin_bp.route("/admin/menu/add", methods=["GET","POST"])
@admin_required
def add_menu():
    if request.method == "POST":
        name_en = request.form.get("name_en")
        name_fi = request.form.get("name_fi")
        price = float(request.form.get("price", "0") or 0)
        category = request.form.get("category", "main")
        active_days = request.form.get("active_days", "")
        dietary = request.form.get("dietary", "{}")
        img = request.form.get("images", "[]")
        doc = {
            "name_en": name_en,
            "name_fi": name_fi,
            "desc_en": request.form.get("desc_en",""),
            "desc_fi": request.form.get("desc_fi",""),
            "price": price,
            "category": category,
            "active_days": [d.strip() for d in active_days.split(",") if d.strip()],
            "dietary": {},
            "images": []
        }
        # try to parse dietary JSON safely
        try:
            import json
            doc["dietary"] = json.loads(dietary) if dietary else {}
            doc["images"] = json.loads(img) if img else []
        except Exception:
            doc["dietary"] = {}
            doc["images"] = []
        db.menu.insert_one(doc)
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/admin_menu_edit.html", item=None)

@admin_bp.route("/admin/menu/edit/<id>", methods=["GET","POST"])
@admin_required
def edit_menu(id):
    item = db.menu.find_one({"_id": ObjectId(id)})
    if not item:
        return "Not found", 404
    # convert ObjectId fields to JSON-friendly where needed in template
    if request.method == "POST":
        # update fields
        update = {
            "name_en": request.form.get("name_en"),
            "name_fi": request.form.get("name_fi"),
            "desc_en": request.form.get("desc_en"),
            "desc_fi": request.form.get("desc_fi"),
            "price": float(request.form.get("price") or 0),
            "category": request.form.get("category"),
            "active_days": [d.strip() for d in (request.form.get("active_days") or "").split(",") if d.strip()],
        }
        try:
            import json
            update["dietary"] = json.loads(request.form.get("dietary") or "{}")
            update["images"] = json.loads(request.form.get("images") or "[]")
        except Exception:
            update["dietary"] = item.get("dietary", {})
            update["images"] = item.get("images", [])
        db.menu.update_one({"_id": ObjectId(id)}, {"$set": update})
        return redirect(url_for("admin.dashboard"))

    # get item into template-friendly format
    item["_id"] = str(item["_id"])
    return render_template("admin/admin_menu_edit.html", item=item)

@admin_bp.route("/announcements")
@admin_required
def announcements_page():
    docs = list(db.announcements.find().sort("start_date",-1))
    for d in docs: d["_id"] = str(d["_id"])
    return render_template("admin/admin_announcements.html", announcements=docs)

@admin_bp.route("/orders")
@admin_required
def orders_page():
    docs = list(db.orders.find().sort("created_at", -1))
    for d in docs: d["_id_str"] = str(d["_id"])
    return render_template("admin/admin_orders.html", orders=docs)
