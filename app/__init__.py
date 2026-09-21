import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ---- Blueprints ----
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp
    from app.routes.wishlist import wishlist_bp
    from app.routes.checkout import checkout_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(wishlist_bp, url_prefix="/wishlist")
    app.register_blueprint(checkout_bp, url_prefix="/checkout")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ---- Template globals ----
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from flask_login import current_user
        from app.models import CartItem, Category

        cart_count = 0
        if current_user.is_authenticated:
            cart_count = sum(
                item.quantity
                for item in CartItem.query.filter_by(user_id=current_user.id).all()
            )

        def nav_categories():
            return Category.query.order_by(Category.name).limit(8).all()

        def now_year():
            return datetime.utcnow().year

        def free_shipping_threshold():
            return app.config["FREE_SHIPPING_THRESHOLD"]

        return {
            "store_name": app.config["STORE_NAME"],
            "currency": app.config["CURRENCY_SYMBOL"],
            "cart_count": cart_count,
            "nav_categories": nav_categories,
            "now_year": now_year,
            "free_shipping_threshold": free_shipping_threshold,
        }

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # ---- CLI ----
    @app.cli.command("seed")
    def seed_command():
        """Seed the database with demo categories and products."""
        from seed import run_seed

        run_seed()
        print("Database seeded.")

    return app
