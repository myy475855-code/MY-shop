from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import Product, Order, OrderItem
from app.routes.misc import admin_required, get_monthly_sales


def admin_routes(app):

    @app.route("/admin/dashboard")
    @login_required
    @admin_required
    def admin_dashboard():
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        sold_items = db.session.query(db.func.sum(OrderItem.quantity)).scalar() or 0
        total_stock = total_products * 10  # Example
        sold_percentage = round((sold_items / total_stock) * 100, 2) if total_stock > 0 else 0
        chart_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        chart_data = get_monthly_sales()
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("dashboard.html",
                               total_products=total_products,
                               total_orders=total_orders,
                               total_revenue=total_revenue,
                               sold_percentage=sold_percentage,
                               chart_labels=chart_labels,
                               chart_data=chart_data,
                               products=products)

    @app.route("/admin/products")
    @login_required
    @admin_required
    def dashboard_products():
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("dashboard_products.html", products=products)


    @app.route("/admin/orders")
    @login_required
    @admin_required
    def dashboard_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return render_template("dashboard_orders.html", orders=orders)

    @app.route("/admin/order/update-status/<int:order_id>", methods=["POST"])
    @login_required
    @admin_required
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get("status")
        if new_status in ["Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Paid"]:
            order.status = new_status
            db.session.commit()
            flash("Order status updated.", "success")
        else:
            flash("Invalid status.", "danger")
        return redirect(url_for("dashboard_orders"))