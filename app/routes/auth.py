from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, make_response
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User
from app.captcha import verify_captcha, render_captcha_png
from app.email_utils import verify_reset_token, send_reset_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/captcha-image")
def captcha_image():
    """Serves a fresh PNG CAPTCHA and stores its code in the session. Never cached."""
    png_buffer = render_captcha_png()
    response = make_response(send_file(png_buffer, mimetype="image/png"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        captcha_answer = request.form.get("captcha_answer", "")

        error = None
        if not name or not email or not password:
            error = "Please fill in all fields."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif not verify_captcha(captcha_answer):
            error = "The code you entered doesn't match the picture — please try again."
        elif User.query.filter_by(email=email).first():
            error = "An account with this email already exists."

        if error:
            flash(error, "error")
            return render_template("auth/register.html", name=name, email=email)

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to MYY SHOP, {user.name.split(' ')[0]}!", "success")
        return redirect(url_for("main.home"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        captcha_answer = request.form.get("captcha_answer", "")

        if not verify_captcha(captcha_answer):
            flash("The code you entered doesn't match the picture — please try again.", "error")
            return render_template("auth/login.html", email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Signed in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.home"))

        flash("Incorrect email or password.", "error")
        return render_template("auth/login.html", email=email)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been signed out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        captcha_answer = request.form.get("captcha_answer", "")

        if not verify_captcha(captcha_answer):
            flash("The code you entered doesn't match the picture — please try again.", "error")
            return render_template("auth/forgot_password.html", email=email)

        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)

        # Same message whether or not the account exists, so we don't leak
        # which emails are registered.
        flash(
            "If an account exists for that email, a password reset link is on its way.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    email = verify_reset_token(token)
    if not email:
        flash("That reset link is invalid or has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("We couldn't find that account.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/reset_password.html", token=token)
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)

        user.set_password(password)
        db.session.commit()
        flash("Your password has been updated. Please sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
