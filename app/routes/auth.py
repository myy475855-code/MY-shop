from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from datetime import datetime, timedelta
import random
from app import db
from app.models import User
from app.routes.misc import send_email

def auth_routes(app):

    @app.route("/register", methods=["GET","POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            if User.query.filter_by(email=email).first():
                flash("Email already registered", "warning")
                return redirect(url_for("register"))

            user = User(
                email=email,
                first_name=request.form.get("firstName"),
                last_name=request.form.get("lastName"),
                phone=request.form.get("phone"),
                country=request.form.get("country"),
                province=request.form.get("province"),
                city=request.form.get("city"),
                address=request.form.get("address"),
                zip_code=request.form.get("zip"),
            )
            user.set_password(request.form.get("password"))
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email").strip().lower()
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(request.form.get("password")):
                login_user(user)
                return redirect(url_for("index"))
            flash("Invalid credentials", "danger")
        return render_template("signin.html")

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/forgot-password", methods=["GET","POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if user:
                code = str(random.randint(100000,999999))
                session["reset_email"] = email
                session["reset_code"] = code
                session["reset_expiry"] = (datetime.utcnow()+timedelta(minutes=10)).isoformat()
                send_email("Reset Code", email, f"Your reset code is {code}")
            return redirect(url_for("verify_code"))
        return render_template("forgot_password.html")

    @app.route("/verify-code", methods=["GET","POST"])
    def verify_code():
        if request.method == "POST":
            if request.form.get("code") == session.get("reset_code"):
                return redirect(url_for("reset_password"))
            flash("Invalid or expired code", "danger")
        return render_template("verify_code.html")

    @app.route("/reset-password", methods=["GET","POST"])
    def reset_password():
        user = User.query.filter_by(email=session.get("reset_email")).first_or_404()
        if request.method == "POST":
            if request.form.get("newPassword") == request.form.get("confirmPassword"):
                user.set_password(request.form.get("newPassword"))
                db.session.commit()
                session.clear()
                return redirect(url_for("login"))
            flash("Passwords do not match", "warning")
        return render_template("reset_password.html")
