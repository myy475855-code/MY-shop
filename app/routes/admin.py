from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models import Product, Order, OrderItem
from app.routes.misc import admin_required, get_monthly_sales

def admin_routes(app):

    @app.route("/admin/dashboard")
    @login_required
    @admin_required
    def admin_dashboard():
        return render_template("dashboard.html",
            total_products=Product.query.count(),
            total_orders=Order.query.count(),
            total_revenue=db.session.query(db.func.sum(Order.total_amount)).scalar() or 0,
            chart_data=get_monthly_sales()
        )

    @app.route("/admin/products")
    @login_required
    @admin_required
    def dashboard_products():
        return render_template("dashboard_products.html",
            products=Product.query.all())

    @app.route("/admin/orders")
    @login_required
    @admin_required
    def dashboard_orders():
        return render_template("dashboard_orders.html",
            orders=Order.query.all())
