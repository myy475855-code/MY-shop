import random
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from app import db
from app.models import CartItem, Address, Order, OrderItem

checkout_bp = Blueprint("checkout", __name__)


def _generate_order_number():
    while True:
        candidate = "ORD-" + "".join(random.choices(string.digits, k=6))
        if not Order.query.filter_by(order_number=candidate).first():
            return candidate


@checkout_bp.route("/", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect(url_for("main.shop"))

    addresses = Address.query.filter_by(user_id=current_user.id).all()

    subtotal = sum(item.line_total for item in items)
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    shipping = 0 if subtotal >= threshold else current_app.config["STANDARD_SHIPPING_FEE"]
    total = subtotal + shipping

    if request.method == "POST":
        address_id = request.form.get("address_id")
        if not address_id:
            flash("Please choose or add a delivery address.", "error")
            return render_template(
                "checkout.html", items=items, addresses=addresses,
                subtotal=subtotal, shipping=shipping, total=total,
            )

        address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
        if not address:
            flash("That address could not be found.", "error")
            return redirect(url_for("checkout.checkout"))

        # Validate stock hasn't changed since the cart was filled
        for item in items:
            if item.quantity > item.product.stock:
                flash(f"Only {item.product.stock} left of {item.product.name}. Please update your cart.", "error")
                return redirect(url_for("cart.view_cart"))

        order = Order(
            order_number=_generate_order_number(),
            user_id=current_user.id,
            address_id=address.id,
            subtotal=subtotal,
            shipping_fee=shipping,
            total=total,
            payment_method="Cash on Delivery",
            status="Pending",
        )
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        for item in items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product.id,
                    product_name=item.product.name,
                    unit_price=item.product.current_price,
                    quantity=item.quantity,
                )
            )
            item.product.stock -= item.quantity
            db.session.delete(item)

        db.session.commit()
        flash("Your order has been placed!", "success")
        return redirect(url_for("orders.order_confirmation", order_number=order.order_number))

    return render_template(
        "checkout.html", items=items, addresses=addresses,
        subtotal=subtotal, shipping=shipping, total=total,
    )
