from flask import render_template, request, flash, redirect, url_for
from flask_mail import Message
from app import mail

def contact_routes(app):
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            email = request.form.get("email")
            message = request.form.get("message")
            if not email or not message:
                flash("Enter both email and message.", "warning")
                return redirect(request.referrer or url_for("contact"))

            text_body = f"From: {email}\n\nMessage:\n{message}"
            html_body = f"<p><b>From:</b> {email}</p><p>{message}</p>"

            msg = Message(subject="New Contact Message",
                          recipients=["myy502388@gmail.com"],
                          body=text_body,
                          html=html_body)
            try:
                mail.send(msg)
                flash("Message sent successfully!", "success")
            except:
                flash("Error sending message.", "danger")

            return redirect(request.referrer or url_for("index"))


        return render_template("contact.html")
