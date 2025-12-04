from functools import wraps
from flask import session, redirect, url_for, request, current_app
from bson import ObjectId
from .db import db

def is_admin_session():
    admin_id = session.get("admin_id")
    if not admin_id:
        return False
    try:
        doc = db.admins.find_one({"_id": ObjectId(admin_id)})
        return bool(doc)
    except Exception:
        return False

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not is_admin_session():
            # preserve next param
            return redirect(url_for("auth.admin_login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper
