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

    # Flask-Mail (used for password reset emails)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME or "no-reply@myyshop.com")

    # If no mail credentials are set, don't let Flask-Mail try to actually
    # connect to an SMTP server (it would just error out). Instead the reset
    # link is logged to the console so local development still works.
    MAIL_SUPPRESS_SEND = MAIL_USERNAME is None

    # Password reset links expire after this many seconds (1 hour)
    RESET_TOKEN_MAX_AGE = 3600
