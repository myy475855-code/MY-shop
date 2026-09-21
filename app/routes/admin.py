from functools import wraps
import os

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Product, Category, Order, User, OrderItem, ORDER_STATUSES, slugify

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(404)
        return view(*args, **kwargs)
    return wrapped


def _allowed_image(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def _save_product_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not _allowed_image(file_storage.filename):
        flash("Image must be png, jpg, jpeg, webp, or gif.", "error")
        return None

    filename = secure_filename(file_storage.filename)
    unique_name = f"{os.urandom(4).hex()}_{filename}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))
    return unique_name


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_sales = db.session.query(db.func.coalesce(db.func.sum(Order.total), 0)).filter(
        Order.status != "Cancelled"
    ).scalar()
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.stock > 0, Product.stock <= 5).all()
    out_of_stock = Product.query.filter(Product.stock <= 0).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        total_sales=total_sales,
        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        recent_orders=recent_orders,
    )


# ---------------- Products ----------------

@admin_bp.route("/products")
@login_required
@admin_required
def product_list():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
@admin_required
def product_new():
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "0").strip()
        sale_price = request.form.get("sale_price", "").strip()
        stock = request.form.get("stock", "0").strip()
        category_id = request.form.get("category_id") or None
        description = request.form.get("description", "").strip()

        if not name or not price:
            flash("Name and price are required.", "error")
            return render_template("admin/product_form.html", categories=categories, product=None)

        product = Product(
            name=name,
            price=float(price),
            sale_price=float(sale_price) if sale_price else None,
            stock=int(stock or 0),
            category_id=int(category_id) if category_id else None,
            description=description,
        )

        image_file = request.files.get("image")
        saved_name = _save_product_image(image_file)
        if saved_name:
            product.image_filename = saved_name

        db.session.add(product)
        db.session.commit()
        flash(f"{product.name} added.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin/product_form.html", categories=categories, product=None)


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.price = float(request.form.get("price") or 0)
        sale_price = request.form.get("sale_price", "").strip()
        product.sale_price = float(sale_price) if sale_price else None
        product.stock = int(request.form.get("stock") or 0)
        category_id = request.form.get("category_id") or None
        product.category_id = int(category_id) if category_id else None
        product.description = request.form.get("description", "").strip()
        product.is_active = bool(request.form.get("is_active"))

        image_file = request.files.get("image")
        saved_name = _save_product_image(image_file)
        if saved_name:
            product.image_filename = saved_name

        db.session.commit()
        flash(f"{product.name} updated.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin/product_form.html", categories=categories, product=product)


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.product_list"))


# ---------------- Categories ----------------

@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def category_list():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name and not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name, slug=slugify(name)))
            db.session.commit()
            flash("Category added.", "success")
        else:
            flash("Category name is required and must be unique.", "error")
        return redirect(url_for("admin.category_list"))

    categories = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=categories)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("Category removed.", "info")
    return redirect(url_for("admin.category_list"))


# ---------------- Orders ----------------

@admin_bp.route("/orders")
@login_required
@admin_required
def order_list():
    status_filter = request.args.get("status", "")
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders, statuses=ORDER_STATUSES, status_filter=status_filter)


@admin_bp.route("/orders/<order_number>")
@login_required
@admin_required
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template("admin/order_detail.html", order=order, statuses=ORDER_STATUSES)


@admin_bp.route("/orders/<order_number>/status", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    new_status = request.form.get("status")

    if new_status in ORDER_STATUSES:
        if new_status == "Cancelled" and order.status != "Cancelled":
            for item in order.items:
                if item.product_id:
                    item.product.stock += item.quantity
        order.status = new_status
        db.session.commit()
        flash(f"Order {order.order_number} marked as {new_status}.", "success")

    return redirect(url_for("admin.order_detail", order_number=order.order_number))


# ---------------- Customers ----------------

@admin_bp.route("/customers")
@login_required
@admin_required
def customer_list():
    customers = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template("admin/customers.html", customers=customers)
