# app/__init__.py
import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from flask_mail import Mail

# --- Extensions ---
db = SQLAlchemy()
login_manager = LoginManager()
serializer = None
mail = Mail()  # Flask-Mail instance

def create_app():
    # --- Load environment variables ---
    load_dotenv()
    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # --- Initialize Flask app ---
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # --- App Config ---
    app.config["SECRET_KEY"] = os.environ.get("MYSHOP_SECRET", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR/'myshop.db'}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB

    # --- Flask-Mail Config ---
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "False") == "True"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
        "MAIL_DEFAULT_SENDER", "no-reply@myshop.local"
    )
    app.config["MAIL_DEBUG"] = True

    # --- Initialize extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    # --- Serializer for token-based operations ---
    global serializer
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # --- User loader for Flask-Login ---
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Register all routes ---
    from app import routes
    routes.register_routes(app)

    # --- Create database tables if they don't exist ---
    with app.app_context():
        db.create_all()

    return app
