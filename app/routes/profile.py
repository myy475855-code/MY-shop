from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
import os

def profile_routes(app):

    @app.route("/profile", methods=["GET","POST"])
    @login_required
    def profile():
        if request.method == "POST":
            current_user.first_name = request.form.get("firstName")
            current_user.last_name = request.form.get("lastName")
            current_user.phone = request.form.get("phone")
            db.session.commit()
        return render_template("profile.html", user=current_user)

    @app.route("/profile/change-location", methods=["POST"])
    @login_required
    def change_location():
        current_user.country = request.form.get("country")
        current_user.province = request.form.get("province")
        current_user.city = request.form.get("city")
        current_user.zip_code = request.form.get("zip_code")
        current_user.address = request.form.get("address")
        db.session.commit()
        return redirect(url_for("profile"))

    @app.route("/change-photo", methods=["POST"])
    @login_required
    def change_photo():
        photo = request.files.get("photo")
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            current_user.photo = filename
            db.session.commit()
        return redirect(url_for("profile"))
