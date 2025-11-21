import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

# --- Extensions ---
db = SQLAlchemy()
login_manager = LoginManager()
serializer = None


def create_app():
    load_dotenv()

    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__, static_folder="static", template_folder="templates")

    # --- Config ---
    app.config["SECRET_KEY"] = os.environ.get("MYSHOP_SECRET", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR/'myshop.db'}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB limit

    # --- Mail Config ---
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT") or 587)
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@myshop.local")

    # --- Initialize extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    global serializer
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # --- Register routes ---
    from app import routes
    routes.register_routes(app)

    with app.app_context():
        db.create_all()

    return app
