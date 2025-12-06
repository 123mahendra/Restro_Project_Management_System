from flask import Flask, Blueprint, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from cart_routes import cart_bp
load_dotenv()



app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your-secret-key"
CORS(app)

from auth_routes import auth_bp, seed_admin_if_needed
from admin_routes import admin_bp
from menu_blueprints import menu_bp
from order_routes import order_bp
from api_routes import api_bp

# # MongoDB
# client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
# db = client[os.getenv("DB_NAME", "restaurant_app")]

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(api_bp)

app.register_blueprint(cart_bp)

# Seed admin on first request
@app.before_request
def initialize():
    seed_admin_if_needed()

if __name__ == "__main__":
    app.run(debug=True)
