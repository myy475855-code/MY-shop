import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'myy_shop.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads (product images)
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB per request
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # Store settings
    STORE_NAME = "MYY SHOP"
    CURRENCY_SYMBOL = "Rs. "
    FREE_SHIPPING_THRESHOLD = 5000
    STANDARD_SHIPPING_FEE = 200
