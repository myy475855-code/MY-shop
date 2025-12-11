from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    country = db.Column(db.String(100))
    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    zip_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="user", lazy=True)
    cart_items = db.relationship("Cart", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    specifications = db.Column(db.Text)  # JSON string: {"Weight":"1kg","Size":"M"}
    categories = db.Column(db.String(500))  # comma-separated categories
    price = db.Column(db.Float, default=0.0)
    discount_price = db.Column(db.Float, default=0.0)
    main_image = db.Column(db.String(500))
    image2 = db.Column(db.String(500))
    image3 = db.Column(db.String(500))
    image4 = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship("Cart", backref="product", lazy=True)
    order_items = db.relationship("OrderItem", backref="product", lazy=True)
    comments = db.relationship("Comment", backref="product", lazy=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    shipping = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="Pending")
    payment_method = db.Column(db.String(20), default="cod")  # cod or card
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_name = db.Column(db.String(255))
    unit_price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)
    discount_price = db.Column(db.Float, default=0.0)  # store discounted price if applicable


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(120))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
