from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from app import db
from app.models import CartItem, Product

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.line_total for item in items)
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    shipping = 0 if (subtotal == 0 or subtotal >= threshold) else current_app.config["STANDARD_SHIPPING_FEE"]
    total = subtotal + shipping
    return render_template(
        "cart.html",
        items=items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        threshold=threshold,
    )


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.in_stock:
        flash(f"{product.name} is out of stock.", "error")
        return redirect(request.referrer or url_for("main.shop"))

    quantity = max(1, int(request.form.get("quantity", 1)))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing:
        existing.quantity = min(existing.quantity + quantity, product.stock)
    else:
        db.session.add(
            CartItem(user_id=current_user.id, product_id=product.id, quantity=min(quantity, product.stock))
        )

    db.session.commit()
    flash(f"Added {product.name} to your cart.", "success")
    return redirect(request.referrer or url_for("main.shop"))


@cart_bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = int(request.form.get("quantity", 1))

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = min(quantity, item.product.stock)

    db.session.commit()
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))
