from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Order, ORDER_STATUSES

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@login_required
def order_list():
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<order_number>")
@login_required
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template("orders/detail.html", order=order, statuses=ORDER_STATUSES)


@orders_bp.route("/<order_number>/confirmation")
@login_required
def order_confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template("orders/confirmation.html", order=order)


@orders_bp.route("/<order_number>/cancel", methods=["POST"])
@login_required
def cancel_order(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()

    if order.status in ("Pending", "Confirmed"):
        order.status = "Cancelled"
        for item in order.items:
            if item.product_id:
                item.product.stock += item.quantity
        db.session.commit()
        flash("Order cancelled.", "info")
    else:
        flash("This order can no longer be cancelled.", "error")

    return redirect(url_for("orders.order_detail", order_number=order.order_number))
