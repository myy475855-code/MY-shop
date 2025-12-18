from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Cart

def cart_routes(app):

    @app.route("/cart")
    @login_required
    def cart():
        items = Cart.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product.price * item.quantity for item in items)
        return render_template("cart.html", items=items, total=total)

    @app.route("/cart/add/<int:product_id>", methods=["POST"])
    @login_required
    def cart_add(product_id):
        qty = int(request.form.get("quantity", 1))
        item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if item:
            item.quantity += qty
        else:
            db.session.add(Cart(user_id=current_user.id, product_id=product_id, quantity=qty))
        db.session.commit()
        return redirect(request.referrer or url_for("cart"))

    @app.route("/cart/update", methods=["POST"])
    @login_required
    def cart_update():
        for key, value in request.form.items():
            if key.startswith("qty_"):
                pid = int(key.replace("qty_", ""))
                item = Cart.query.filter_by(user_id=current_user.id, product_id=pid).first()
                if item:
                    item.quantity = int(value)
        db.session.commit()
        return redirect(url_for("cart"))

    @app.route("/cart/remove/<int:item_id>")
    @login_required
    def cart_remove(item_id):
        item = Cart.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for("cart"))
