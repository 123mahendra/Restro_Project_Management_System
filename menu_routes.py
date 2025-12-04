from flask import Blueprint, request, redirect, render_template, jsonify
from bson import ObjectId

from app import db
from utils.auth import admin_required

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("/menu")
def menu_page():
    items = list(db.menu.find({"visible": True}).sort([("category", 1), ("name_en", 1)]))
    for it in items:
        it["_id"] = str(it["_id"])
    return render_template("menu.html", items=items)

# optional public API endpoint (keeps previous client usage)
@menu_bp.route("/api/menu_public")
def menu_public_api():
    q = {}
    category = request.args.get("category")
    if category:
        q["category"] = category
    items = list(db.menu.find(q).sort([("category", 1), ("name_en", 1)]))
    for it in items:
        it["_id"] = str(it["_id"])
    return jsonify(items)

# # --- ADD MENU ITEM ---
# @menu_bp.route("/menu", methods=["POST"])
# @admin_required
# def add_menu():
#     data = {
#         "name_fi": request.form.get("name_fi"),
#         "name_en": request.form.get("name_en"),
#         "price": float(request.form.get("price")),
#         "day": request.form.get("day"),
#         "diet": request.form.get("diet")
#     }
#     db.menu.insert_one(data)
#     return redirect("/admin/dashboard")

#
# # --- DELETE ITEM ---
# @menu_bp.route("/admin/menu/delete/<id>")
# @admin_required
# def delete_item(id):
#     db.menu.delete_one({"_id": ObjectId(id)})
#     return redirect("/admin/dashboard")


# # --- EDIT ITEM ---
# @menu_bp.route("/admin/menu/edit/<id>", methods=["GET", "POST"])
# @admin_required
# def edit_menu(id):
#     item = db.menu.find_one({"_id": ObjectId(id)})
#
#     if request.method == "POST":
#         db.menu.update_one(
#             {"_id": ObjectId(id)},
#             {"$set": {
#                 "name_fi": request.form.get("name_fi"),
#                 "name_en": request.form.get("name_en"),
#                 "price": float(request.form.get("price")),
#                 "day": request.form.get("day"),
#                 "diet": request.form.get("diet")
#             }}
#         )
#         return redirect("/admin/dashboard")
#
#     return render_template("admin_menu_edit.html", item=item)
