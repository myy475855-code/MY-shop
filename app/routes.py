# app/routes.py
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os, uuid, random
from datetime import datetime, timedelta
from app import db, login_manager, mail
from app.models import User, Product, Cart, Order, OrderItem, Comment
from flask_mail import Message

# ----------------- User Loader -----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- Helper Functions -----------------
def generate_order_number():
    return str(uuid.uuid4()).replace("-", "").upper()[:12]

def send_email(subject, to, body_text, body_html=None):
    """Send email using Flask-Mail"""
    try:
        msg = Message(subject=subject, recipients=[to])
        msg.body = body_text
        if body_html:
            msg.html = body_html
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != "myy502388@gmail.com":
            flash("Admin access required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def get_monthly_sales():
    """Return monthly sales totals"""
    monthly_sales = []
    for month in range(1, 13):
        total = db.session.query(db.func.sum(Order.total_amount)) \
            .filter(db.extract("month", Order.created_at) == month).scalar() or 0
        monthly_sales.append(round(total, 2))
    return monthly_sales

# ----------------- Register Routes -----------------
def register_routes(app):

    # -------- Home / Index --------
    @app.route("/")
    def index():
        products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
        return render_template("index.html", products=products)

    # -------- Register --------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            if not email:
                flash("Email is required", "danger")
                return redirect(url_for("register"))
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
            password = request.form.get("password")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    # -------- Login --------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for("index"))
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))
        return render_template("signin.html")

    # -------- Logout --------
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    # -------- Profile --------
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if request.method == "POST":
            current_user.first_name = request.form.get("firstName")
            current_user.last_name = request.form.get("lastName")
            current_user.phone = request.form.get("phone")
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
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
        flash("Location updated.", "success")
        return redirect(url_for("profile"))

    # -------- Upload Product --------
    @app.route("/upload-product", methods=["GET", "POST"])
    @login_required
    @admin_required
    def upload_product():
        if request.method == "POST":
            name = request.form.get("product_name")
            description = request.form.get("description")
            price = float(request.form.get("price") or 0)
            discounted_price = request.form.get("discounted_price")
            discounted_price = float(discounted_price) if discounted_price else None

            categories = request.form.getlist("categories[]")
            categories = ",".join(categories)

            spec_names = request.form.getlist("spec_name[]")
            spec_values = request.form.getlist("spec_type[]")
            simple_specs = [f"{n}: {v}" for n, v in zip(spec_names, spec_values) if n and v]
            specifications = "\n".join(simple_specs)

            images = [request.files.get(f"image{i}") for i in range(1, 5)]
            filenames = []
            for img in images:
                if img and img.filename != "":
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    filenames.append(filename)
                else:
                    filenames.append(None)

            product = Product(
                name=name,
                description=description,
                specifications=specifications,
                categories=categories,
                price=price,
                discount_price=discounted_price,
                main_image=filenames[0],
                image2=filenames[1],
                image3=filenames[2],
                image4=filenames[3],
            )
            db.session.add(product)
            db.session.commit()
            flash("Product uploaded successfully!", "success")
            return redirect(url_for("upload_product"))
        return render_template("upload.html")

    # -------- Products Listing --------
    @app.route("/products")
    def products():
        page = int(request.args.get("page", 1))
        per_page = 12
        pag = Product.query.order_by(Product.created_at.desc()).paginate(page, per_page, error_out=False)
        return render_template("products.html", pagination=pag)

    # -------- Product Detail / Comments --------
    @app.route("/product/<int:product_id>", methods=["GET", "POST"])
    def product_detail(product_id):
        product = Product.query.get_or_404(product_id)

        # Handle comments
        if request.method == "POST":
            body = request.form.get("comment")
            if body:
                comment = Comment(
                    product_id=product.id,
                    user_id=current_user.get_id() if current_user.is_authenticated else None,
                    name=current_user.first_name if current_user.is_authenticated else request.form.get("name") or "Guest",
                    content=body
                )
                db.session.add(comment)
                db.session.commit()
                flash("Comment posted!", "success")
            return redirect(request.url)

        # Parse categories (stored as comma-separated)
        categories = product.categories.split(",") if product.categories else []

        # Parse specifications (stored as newline-separated)
        specifications = product.specifications.split("\n") if product.specifications else []

        # Collect images safely
        images = [
            img for img in [
                product.main_image,
                product.image2,
                product.image3,
                product.image4
            ] if img
        ]

        # Get comments
        comments = (
            Comment.query
            .filter_by(product_id=product.id)
            .order_by(Comment.created_at.desc())
            .all()
        )

        return render_template(
            "product_detail.html",
            product=product,
            images=images,
            categories=categories,
            specifications=specifications,
            comments=comments
        )


    # -------- Cart --------
    @app.route("/cart/add/<int:product_id>", methods=["POST"])
    @login_required
    def cart_add(product_id):
        qty = int(request.form.get("quantity", 1))
        item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if item:
            item.quantity += qty
        else:
            item = Cart(user_id=current_user.id, product_id=product_id, quantity=qty)
            db.session.add(item)
        db.session.commit()
        flash("Product added to cart!", "success")
        return redirect(request.referrer or url_for("cart"))

    @app.route("/cart")
    @login_required
    def cart():
        items = Cart.query.filter_by(user_id=current_user.id).all()
        total = sum((item.product.price or 0) * item.quantity for item in items)
        return render_template("cart.html", items=items, total=total)

    @app.route("/cart/remove/<int:item_id>")
    @login_required
    def cart_remove(item_id):
        item = Cart.query.get_or_404(item_id)
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash("Item removed from cart.", "info")
        return redirect(url_for("cart"))

    # -------- Contact (Flask-Mail) --------
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            email = request.form.get("email")
            message = request.form.get("message")
            if not email or not message:
                flash("Enter both email and message.", "warning")
                return redirect(request.referrer or url_for("index"))

            text_body = f"From: {email}\n\nMessage:\n{message}"
            html_body = f"<h3>New Contact Message</h3><p><b>From:</b> {email}</p><p>{message}</p>"

            send_email("New Contact Message", "myy502388@gmail.com", text_body, html_body)
            flash("Message sent successfully!", "success")
            return redirect(request.referrer or url_for("index"))

        return render_template("contact.html")

    # -------- Forgot / Reset Password (Flask-Mail) --------
    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if user:
                code = str(random.randint(100000, 999999))
                session["reset_email"] = email
                session["reset_code"] = code
                session["reset_expiry"] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

                text_body = f"Your password reset code is: {code}"
                html_body = f"<h2>Password Reset Code</h2><p>Your verification code is <b>{code}</b>. It expires in 10 minutes.</p>"

                send_email("Reset Code", email, text_body, html_body)

            flash("If the account exists, a verification code was sent.", "info")
            return redirect(url_for("verify_code"))
        return render_template("forgot_password.html")

    @app.route("/verify-code", methods=["GET", "POST"])
    def verify_code():
        if request.method == "POST":
            code = request.form.get("code")
            saved_code = session.get("reset_code")
            expiry = datetime.fromisoformat(session.get("reset_expiry"))
            if code == saved_code and datetime.utcnow() <= expiry:
                flash("Code verified.", "success")
                return redirect(url_for("reset_password"))
            flash("Invalid or expired code.", "danger")
            return redirect(url_for("verify_code"))
        return render_template("verify_code.html")

    @app.route("/reset-password", methods=["GET", "POST"])
    def reset_password():
        email = session.get("reset_email")
        if not email:
            flash("Session expired.", "danger")
            return redirect(url_for("forgot_password"))
        user = User.query.filter_by(email=email).first_or_404()
        if request.method == "POST":
            new = request.form.get("newPassword")
            confirm = request.form.get("confirmPassword")
            if new and new == confirm:
                user.set_password(new)
                db.session.commit()
                session.pop("reset_email", None)
                session.pop("reset_code", None)
                session.pop("reset_expiry", None)
                flash("Password reset successful.", "success")
                return redirect(url_for("login"))
            flash("Passwords do not match.", "warning")
            return redirect(request.url)
        return render_template("reset_password.html", user=user)

    # -------- Checkout / Orders (Flask-Mail) --------
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
                flash("Select a payment method.", "danger")
                return redirect(url_for("cart_confirm"))
            session["payment_method"] = payment_method
            return redirect(url_for("cart_checkout"))
        return render_template("confirm_order.html", items=items, total=total, user=current_user)

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

        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            total_amount=total_amount,
            shipping=shipping_fee,
            status=order_status
        )
        db.session.add(order)
        db.session.commit()

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
            db.session.delete(item)
        db.session.commit()

        # Send order confirmation email to admin
        order_details_html = "<br>".join([f"{oi.product_name} x {oi.quantity} = ${oi.unit_price * oi.quantity:.2f}" for oi in order.items])
        text_body = f"New order confirmed!\nOrder Number: {order.order_number}\nCustomer: {current_user.first_name} {current_user.last_name}\nEmail: {current_user.email}\nTotal Amount: ${order.total_amount:.2f}\nPayment Method: {payment_method}\nItems:\n" + "\n".join([f"{oi.product_name} x {oi.quantity} = ${oi.unit_price * oi.quantity:.2f}" for oi in order.items])
        html_body = f"""
        <h2>New Order Confirmed</h2>
        <p><b>Order Number:</b> {order.order_number}</p>
        <p><b>Customer:</b> {current_user.first_name} {current_user.last_name}</p>
        <p><b>Email:</b> {current_user.email}</p>
        <p><b>Total Amount:</b> ${order.total_amount:.2f}</p>
        <p><b>Payment Method:</b> {payment_method}</p>
        <h3>Items:</h3>
        <p>{order_details_html}</p>
        """
        send_email("New Order Confirmed - MyShop", "myy502388@gmail.com", text_body, html_body)

        flash("Order placed successfully!", "success")
        return redirect(url_for("order_confirmation", order_id=order.id))

    @app.route("/order/<int:order_id>/confirmation")
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)
        return render_template("order.html", order=order)

    @app.route("/orders")
    @login_required
    def orders():
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template("orders.html", orders=orders)

    # -------- Search --------
    @app.route("/search")
    def search():
        q = request.args.get("q", "").strip()
        products = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%")) |
            (Product.categories.ilike(f"%{q}%"))
        ).all() if q else []
        return render_template("search_results.html", products=products, query=q)

    # -------- Admin Dashboard --------
    @app.route("/admin/dashboard")
    @login_required
    @admin_required
    def admin_dashboard():
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        sold_items = db.session.query(db.func.sum(OrderItem.quantity)).scalar() or 0
        total_stock = total_products * 10  # Example
        sold_percentage = round((sold_items / total_stock) * 100, 2) if total_stock > 0 else 0
        chart_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        chart_data = get_monthly_sales()
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("dashboard.html",
                               total_products=total_products,
                               total_orders=total_orders,
                               total_revenue=total_revenue,
                               sold_percentage=sold_percentage,
                               chart_labels=chart_labels,
                               chart_data=chart_data,
                               products=products)

    @app.route("/admin/products")
    @login_required
    @admin_required
    def dashboard_products():
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("dashboard_products.html", products=products)

    @app.route("/admin/product/edit/<int:product_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            product.name = request.form.get("product_name")
            product.description = request.form.get("description")
            product.specifications = request.form.get("specifications")
            categories = request.form.getlist("categories")
            product.categories = ",".join([c for c in categories if c])
            product.price = float(request.form.get("price") or 0.0)
            for key in ["image1","image2","image3","image4"]:
                file = request.files.get(key)
                if file and file.filename != "":
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    setattr(product, key if key!="image1" else "main_image", filename)
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("dashboard_products"))
        return render_template("edit_product.html", product=product)

    @app.route("/admin/product/delete/<int:product_id>")
    @login_required
    @admin_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully!", "info")
        return redirect(url_for("dashboard_products"))

    @app.route("/admin/orders")
    @login_required
    @admin_required
    def dashboard_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return render_template("dashboard_orders.html", orders=orders)

    @app.route("/admin/order/update-status/<int:order_id>", methods=["POST"])
    @login_required
    @admin_required
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get("status")
        if new_status in ["Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Paid"]:
            order.status = new_status
            db.session.commit()
            flash("Order status updated.", "success")
        else:
            flash("Invalid status.", "danger")
        return redirect(url_for("dashboard_orders"))

    # -------- Error Handlers --------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("500.html"), 500