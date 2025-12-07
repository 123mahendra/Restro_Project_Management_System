from flask import Flask, Blueprint, render_template, request, redirect, make_response, get_flashed_messages, flash
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
from db import create_user,get_database
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your-secret-key"
CORS(app)



users = [
    {
        "id": "1",
        "first_name": "Admin",
        "last_name": "Admin",
        "email": "admin@admin.com",
        "password": "admin@admin",
        "role": "admin"
    }
]

sessions = {}

# Default home route

@app.route('/')
def home():
    user = None
    if "user_id" in session:
        user = {"first_name": session.get("user_first_name"),"last_name": session.get("user_last_name")}
    return render_template("index.html", user=user)

# Login Route

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/user/login', methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        db = get_database()
       
        user = db.users.find_one({"email": user_email})
        if not user:
            flash("Email not found!", "error")
            return redirect('/login')

        if not check_password_hash(user["password"], user_password):
            flash("Incorrect password!", "error")
            return redirect('/login')

        # Create session
        session["user_id"] = str(user["_id"])
        session["user_first_name"] = user["first_name"]
        session["user_last_name"] = user["last_name"]

        return redirect('/')

    return render_template("login.html")

# Logout Route

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect('/login')


# Register Route

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        user_email = request.form.get("email")

        db = get_database()

        # Check if email already exists
        existing_user = db.users.find_one({"email": user_email})
        if existing_user:
            flash("Email already registered!", "error")
            return redirect("/login")

        user_password = request.form.get("password")
        hashed_password = generate_password_hash(user_password)
        new_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_email,
            "password": hashed_password,
            "role":"user"
        }
        create_user(new_user)
        flash("User register successfully!", "success")
        return redirect('/login')
        
# Admin Routes

@app.route('/admin')
def admin():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id in sessions:
        return redirect("/admin/dashboard")
    return render_template("admin/admin_login.html")


@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")

        for user in users:
            if (user_email == user["email"] 
                and user_password == user["password"] 
                and user['role'] == 'admin'):
                
                user_session_id = str(uuid.uuid4())
                sessions[user_session_id] = user
                
                resp = make_response(redirect("/admin/dashboard"))
                resp.set_cookie("user_session_id", user_session_id)
                return resp
            
        flash("Invalid email or password!", "error")
        return redirect("/admin")
    
    return render_template("admin/admin_login.html")


@app.route('/admin/dashboard')
def admin_dashboard():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id not in sessions:
        return redirect("/admin")

    user = sessions[user_session_id]
    return render_template("admin/admin_dashboard.html", user=user)


@app.route('/admin/logout')
def admin_logout():
    user_session_id = request.cookies.get("user_session_id")
    if user_session_id in sessions:
        sessions.pop(user_session_id)
        
    resp = make_response(redirect("/admin"))
    resp.set_cookie("user_session_id", '', expires=0, path='/')
    return resp

if __name__ == "__main__":
    app.run(debug=True)
