from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import WishlistItem, Product, CartItem

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/")
@login_required
def view_wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template("wishlist.html", items=items)


@wishlist_bp.route("/toggle/<int:product_id>", methods=["POST"])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash(f"Removed {product.name} from your wishlist.", "info")
    else:
        db.session.add(WishlistItem(user_id=current_user.id, product_id=product.id))
        db.session.commit()
        flash(f"Added {product.name} to your wishlist.", "success")

    return redirect(request.referrer or url_for("main.shop"))


@wishlist_bp.route("/move-to-cart/<int:item_id>", methods=["POST"])
@login_required
def move_to_cart(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=item.product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=item.product_id, quantity=1))

    db.session.delete(item)
    db.session.commit()
    flash("Moved to your cart.", "success")
    return redirect(url_for("wishlist.view_wishlist"))
