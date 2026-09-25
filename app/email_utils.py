from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, url_for
from flask_mail import Message

from app import mail

RESET_SALT = "myy-shop-password-reset"


def generate_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(user.email, salt=RESET_SALT)


def verify_reset_token(token):
    """Return the email address encoded in the token, or None if it's invalid/expired."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    max_age = current_app.config.get("RESET_TOKEN_MAX_AGE", 3600)
    try:
        return serializer.loads(token, salt=RESET_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def send_reset_email(user):
    token = generate_reset_token(user)
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    store_name = current_app.config["STORE_NAME"]

    text_body = (
        f"Hi {user.name},\n\n"
        f"Someone requested a password reset for your {store_name} account.\n"
        f"Click the link below to choose a new password. This link expires in 1 hour.\n\n"
        f"{reset_url}\n\n"
        f"If you didn't request this, you can safely ignore this email.\n"
    )

    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        # No SMTP credentials configured — log the link so local dev/testing still works.
        current_app.logger.info(
            "MAIL_SUPPRESS_SEND is on (no MAIL_USERNAME set). "
            "Password reset link for %s: %s", user.email, reset_url
        )
        return reset_url

    msg = Message(
        subject=f"Reset your {store_name} password",
        recipients=[user.email],
        body=text_body,
    )
    mail.send(msg)
    return reset_url


def send_order_confirmation_email(order):
    user = order.user
    store_name = current_app.config["STORE_NAME"]
    currency = current_app.config["CURRENCY_SYMBOL"]

    lines = [f"  - {item.product_name} x{item.quantity}: {currency}{item.line_total:,.0f}" for item in order.items]
    items_block = "\n".join(lines)

    text_body = (
        f"Hi {user.name},\n\n"
        f"Thanks for your order! Here's your confirmation for {order.order_number}.\n\n"
        f"Items:\n{items_block}\n\n"
        f"Subtotal: {currency}{float(order.subtotal):,.0f}\n"
        f"Shipping: {'Free' if float(order.shipping_fee) == 0 else currency + f'{float(order.shipping_fee):,.0f}'}\n"
        f"Total: {currency}{float(order.total):,.0f}\n\n"
        f"Payment method: {order.payment_method}\n"
        f"Delivering to: {order.address.full_name}, {order.address.address_line}, {order.address.location_line}\n\n"
        f"We'll let you know as your order moves through Confirmed, Processing, Shipped, and Delivered.\n\n"
        f"Thanks for shopping with {store_name}!\n"
    )

    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        current_app.logger.info(
            "MAIL_SUPPRESS_SEND is on (no MAIL_USERNAME set). "
            "Order confirmation email for %s (order %s) was not actually sent.",
            user.email, order.order_number,
        )
        return

    msg = Message(
        subject=f"Your {store_name} order {order.order_number} is confirmed",
        recipients=[user.email],
        body=text_body,
    )
    mail.send(msg)
