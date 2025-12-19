from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from flask_mail import Message
from app import mail, db
from app.models import Order

def send_email(subject, to, body):
    mail.send(Message(subject=subject, recipients=[to], body=body))

def generate_order_number():
    import uuid
    return str(uuid.uuid4()).replace("-", "").upper()[:12]

def get_monthly_sales():
    sales = []
    for m in range(1,13):
        total = db.session.query(db.func.sum(Order.total_amount))\
            .filter(db.extract("month", Order.created_at)==m).scalar() or 0
        sales.append(total)
    return sales

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != "myy502388@gmail.com":
            flash("Admin access required", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap

def misc_routes(app):

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500
