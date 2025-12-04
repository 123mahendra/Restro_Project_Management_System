# auth_routes.py
import os
import datetime
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import db

auth_bp = Blueprint("auth", __name__)

def seed_admin_if_needed():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")

    existing = db.admins.find_one({"username": admin_username})
    if existing:
        return

    pw_hash = generate_password_hash(admin_password)
    doc = {
        "username": admin_username,
        "password": pw_hash,
        "email": admin_email,
        "created_at": datetime.datetime.utcnow()
    }
    res = db.admins.insert_one(doc)
    current_app.logger.info("Seeded admin user: %s", admin_username)
    return res.inserted_id

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = db.admins.find_one({"username": username})
        if not admin or not check_password_hash(admin["password"], password):
            flash("Invalid username or password", "danger")
            return render_template("admin/admin_login.html", error="Invalid credentials")
        session["admin_id"] = str(admin["_id"])
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/admin_login.html")

@auth_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("auth.admin_login"))
