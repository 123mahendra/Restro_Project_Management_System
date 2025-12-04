from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

from auth_routes import auth_bp, seed_admin_if_needed
from admin_routes import admin_bp
from menu_routes import menu_bp
from order_routes import order_bp
from api_routes import api_bp

app = Flask(__name__, template_folder="pages", static_folder="static")
app.secret_key = "your-secret-key"
CORS(app)

# MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("DB_NAME", "restaurant_app")]

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(api_bp)

# Seed admin on first request
@app.before_request
def initialize():
    seed_admin_if_needed()

if __name__ == "__main__":
    app.run(debug=True)