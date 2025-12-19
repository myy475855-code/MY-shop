from flask import render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_user, logout_user
from datetime import datetime, timedelta
import random, string, io
from PIL import Image, ImageDraw, ImageFont
from app import db
from app.models import User
from app.routes.misc import send_email

def auth_routes(app):

    # ---------- CAPTCHA IMAGE GENERATOR ----------
    @app.route('/captcha-image')
    def captcha_image():
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        session['captcha'] = text

        img = Image.new('RGB', (150, 60), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        draw.text((20, 10), text, fill=(0, 0, 0), font=font)

        buf = io.BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')


    # ---------- REGISTER ----------
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
            # After register, redirect to CAPTCHA verification page
            session['pending_user'] = email  # Save email to session
            return redirect(url_for("verify_captcha"))
        return render_template("register.html")


    # ---------- LOGIN ----------
    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email").strip().lower()
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(request.form.get("password")):
                # Save logged-in user temporarily to session before CAPTCHA
                session['pending_user'] = email
                return redirect(url_for("verify_captcha"))
            flash("Invalid credentials", "danger")
        return render_template("signin.html")


    # ---------- CAPTCHA VERIFICATION ----------
    @app.route("/verify-captcha", methods=["GET","POST"])
    def verify_captcha():
        if 'pending_user' not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            user_input = request.form.get("captcha", "").strip().upper()
            if user_input == session.get("captcha", "").upper():
                # CAPTCHA correct
                email = session.pop('pending_user')
                user = User.query.filter_by(email=email).first()
                if user:
                    login_user(user)  # log in the user after CAPTCHA
                    flash("✅ CAPTCHA verified. Welcome!", "success")
                    return redirect(url_for("index"))
                flash("User not found", "danger")
                return redirect(url_for("login"))
            flash("❌ CAPTCHA incorrect. Try again.", "danger")
            return redirect(url_for("verify_captcha"))

        return render_template("captcha_page.html")  # separate template


    # ---------- LOGOUT ----------
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))


    # ---------- FORGOT PASSWORD ----------
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


    # ---------- VERIFY CODE ----------
    @app.route("/verify-code", methods=["GET","POST"])
    def verify_code():
        if request.method == "POST":
            if request.form.get("code") == session.get("reset_code"):
                return redirect(url_for("reset_password"))
            flash("Invalid or expired code", "danger")
        return render_template("verify_code.html")


    # ---------- RESET PASSWORD ----------
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
