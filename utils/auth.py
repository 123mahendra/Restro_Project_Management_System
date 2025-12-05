from functools import wraps
from flask import session, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("auth.admin_login"))
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "customer_id" not in session:
            return redirect(url_for("auth.customer_login"))
        return f(*args, **kwargs)
    return decorated

def is_admin_session():
    return "admin_id" in session
