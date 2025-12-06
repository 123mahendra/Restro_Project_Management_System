from flask import Flask, Blueprint, render_template, request, redirect, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import uuid

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

@app.route('/')
def home():
    return render_template("index.html")

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

        return redirect("/admin", error="Invalid credentials")
    
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
