# api_routes.py
import datetime
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from utils.db import db
from utils.auth import admin_required, is_admin_session

api_bp = Blueprint("api", __name__)

# ----------------------
# Helper to convert _id
# ----------------------
def serialize_doc(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_list(lst):
    for d in lst:
        d["_id"] = str(d["_id"])
    return lst

# ----------------------
# Menu endpoints
# ----------------------
@api_bp.route("/api/menu", methods=["GET"])
def get_menu():
    # optional filters: category, vegetarian, vegan, day
    q = {}
    category = request.args.get("category")
    if category:
        q["category"] = category
    if request.args.get("vegetarian") == "1":
        q["dietary.vegetarian"] = True
    if request.args.get("vegan") == "1":
        q["dietary.vegan"] = True
    day = request.args.get("day")
    if day:
        q["active_days"] = {"$in": [day.lower()]}
    docs = list(db.menu.find(q).sort([("category", 1), ("name_en", 1)]))
    serialize_list(docs)
    return jsonify(docs)

@api_bp.route("/api/menu", methods=["POST"])
@admin_required
def create_menu():
    payload = request.json or {}
    # required fields validation
    name_en = payload.get("name_en")
    price = payload.get("price")
    if name_en is None or price is None:
        return jsonify({"error": "name_en and price required"}), 400
    doc = {
        "name_en": name_en,
        "name_fi": payload.get("name_fi", ""),
        "desc_en": payload.get("desc_en", ""),
        "desc_fi": payload.get("desc_fi", ""),
        "price": float(price),
        "category": payload.get("category", "main"),
        "active_days": payload.get("active_days", []),
        "dietary": payload.get("dietary", {}),
        "visible": payload.get("visible", True),
        "images": payload.get("images", []),
        "created_at": datetime.datetime.utcnow()
    }
    res = db.menu.insert_one(doc)
    return jsonify({"_id": str(res.inserted_id)}), 201

@api_bp.route("/api/menu/<id>", methods=["PUT"])
@admin_required
def update_menu(id):
    payload = request.json or {}
    update = {}
    # only set fields present
    for f in ("name_en","name_fi","desc_en","desc_fi","category","images"):
        if f in payload:
            update[f] = payload[f]
    if "price" in payload:
        update["price"] = float(payload["price"])
    if "active_days" in payload:
        update["active_days"] = payload["active_days"]
    if "dietary" in payload:
        update["dietary"] = payload["dietary"]
    if "visible" in payload:
        update["visible"] = bool(payload["visible"])
    if not update:
        return jsonify({"error":"nothing to update"}), 400
    db.menu.update_one({"_id": ObjectId(id)}, {"$set": update})
    return jsonify({"ok": True})

@api_bp.route("/api/menu/<id>", methods=["DELETE"])
@admin_required
def delete_menu(id):
    db.menu.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

# ----------------------
# Announcements endpoints
# ----------------------
@api_bp.route("/api/announcements", methods=["GET"])
def get_announcements():
    today = datetime.date.today()
    docs = list(db.announcements.find({"active": True}).sort("start_date", -1))
    # filter by start/end date if provided
    res = []
    for d in docs:
        start = d.get("start_date")
        end = d.get("end_date")
        ok = True
        if start and isinstance(start, datetime.date):
            ok = ok and (start <= today)
        if end and isinstance(end, datetime.date):
            ok = ok and (end >= today)
        if ok:
            d["_id"] = str(d["_id"])
            res.append(d)
    return jsonify(res)

@api_bp.route("/api/announcements", methods=["POST"])
@admin_required
def create_announcement():
    payload = request.json or {}
    title = payload.get("title")
    content = payload.get("content") or payload.get("message") or payload.get("message", "")
    if not title:
        return jsonify({"error":"title required"}), 400
    doc = {
        "title": title,
        "message": content,
        "start_date": payload.get("start_date"),
        "end_date": payload.get("end_date"),
        "active": bool(payload.get("active", True)),
        "created_at": datetime.datetime.utcnow()
    }
    res = db.announcements.insert_one(doc)
    return jsonify({"_id": str(res.inserted_id)}), 201

@api_bp.route("/api/announcements/<id>", methods=["DELETE"])
@admin_required
def delete_announcement(id):
    db.announcements.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

# ----------------------
# Orders endpoints
# ----------------------
@api_bp.route("/api/orders", methods=["GET"])
def get_orders():
    # if admin -> return all orders, otherwise return empty or filtered (for customer flows)
    if is_admin_session():
        docs = list(db.orders.find().sort("created_at", -1))
    else:
        # for non-admin use-case you would filter by user id (not implemented here)
        return jsonify([])  # or 403 in strict mode
    serialize_list(docs)
    return jsonify(docs)

@api_bp.route("/api/orders/<id>/status", methods=["POST"])
@admin_required
def update_order_status(id):
    payload = request.json or {}
    status = payload.get("status")
    if not status:
        return jsonify({"error":"status required"}), 400
    db.orders.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    return jsonify({"ok": True})
