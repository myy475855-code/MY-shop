from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Cart, Product
from app import db, mail
from flask_mail import Message
import uuid

def order_routes(app):

    # -------- Orders List --------
    @app.route("/orders")
    @login_required
    def orders():
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template("orders.html", orders=orders)

    # -------- Cart Confirm --------
    @app.route("/cart/confirm", methods=["GET", "POST"])
    @login_required
    def cart_confirm():
        items = Cart.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash("Cart is empty.", "warning")
            return redirect(url_for("cart"))

        total = sum((item.product.price or 0) * item.quantity for item in items)

        if request.method == "POST":
            payment_method = request.form.get("payment_method")
            if payment_method not in ["card", "cod"]:
                flash("Select a valid payment method.", "danger")
                return redirect(url_for("cart_confirm"))
            session["payment_method"] = payment_method
            return redirect(url_for("cart_checkout"))

        return render_template("confirm_order.html", items=items, total=total,user=current_user)

    # -------- Cart Checkout --------
    @app.route("/cart/checkout", methods=["GET", "POST"])
    @login_required
    def cart_checkout():
        items = Cart.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash("Cart is empty.", "warning")
            return redirect(url_for("cart"))

        payment_method = session.pop("payment_method", None)
        if not payment_method:
            flash("Confirm your order first.", "warning")
            return redirect(url_for("cart_confirm"))

        total = sum((item.product.price or 0) * item.quantity for item in items)
        shipping_fee = 0.0
        total_amount = total + shipping_fee
        order_status = "Paid" if payment_method == "card" else "Pending"

        # Generate order number
        order_number = str(uuid.uuid4()).replace("-", "").upper()[:12]

        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            total_amount=total_amount,
            shipping=shipping_fee,
            status=order_status,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.commit()

        # Add items to order
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                user_id=current_user.id,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity
            )
            db.session.add(order_item)
            db.session.delete(item)  # remove from cart
        db.session.commit()

        # Send email to admin
        order_details_html = "<br>".join([f"{oi.product_name} x {oi.quantity} = ${oi.unit_price * oi.quantity:.2f}" for oi in order.items])
        text_body = f"New order confirmed!\nOrder Number: {order.order_number}\nCustomer: {current_user.first_name} {current_user.last_name}\nEmail: {current_user.email}\nTotal Amount: ${order.total_amount:.2f}\nPayment Method: {payment_method}\nItems:\n" + "\n".join([f"{oi.product_name} x {oi.quantity} = ${oi.unit_price * oi.quantity:.2f}" for oi in order.items])
        html_body = f"""
        <h2>New Order Confirmed</h2>
        <p><b>Order Number:</b> {order.order_number}</p>
        <p><b>Customer:</b> {current_user.first_name} {current_user.last_name}</p>
        <p><b>Email:</b> {current_user.email}</p>
        <p> <b>Address: </b>{ current_user.address },{ current_user.city },{ current_user.province } - { current_user.country }</p>
        <p><b>ZIP Code:</b> { current_user.zip_code }</p>
        <p><b>Total Amount:</b> ${order.total_amount:.2f}</p>
        <p><b>Payment Method:</b> {payment_method}</p>
        <h3>Items:</h3>
        <p>{order_details_html}</p>
        """
        try:
            msg = Message(subject="New Order Confirmed - MyShop",
                          recipients=["myy502388@gmail.com"],
                          body=text_body,
                          html=html_body)
            mail.send(msg)
        except Exception as e:
            print(f"Email send error: {e}")

        flash("Order placed successfully!", "success")
        return redirect(url_for("order_confirmation", order_id=order.id))

    # -------- Order Confirmation Page --------
    @app.route("/order/<int:order_id>/confirmation")
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)
        return render_template("orders.html", order=order)
