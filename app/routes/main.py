from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Product, Category, Address, WishlistItem, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    featured = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    categories = Category.query.order_by(Category.name).all()
    return render_template("home.html", featured=featured, categories=categories)


@main_bp.route("/shop")
def shop():
    query = Product.query.filter_by(is_active=True)

    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest")

    if q:
        query = query.filter(
            or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        )

    active_category = None
    if category_slug:
        active_category = Category.query.filter_by(slug=category_slug).first()
        if active_category:
            query = query.filter_by(category_id=active_category.id)

    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    categories = Category.query.order_by(Category.name).all()

    wishlist_ids = set()
    if current_user.is_authenticated:
        wishlist_ids = {
            w.product_id for w in WishlistItem.query.filter_by(user_id=current_user.id).all()
        }

    return render_template(
        "products/list.html",
        products=products,
        categories=categories,
        active_category=active_category,
        q=q,
        sort=sort,
        wishlist_ids=wishlist_ids,
    )


@main_bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (
        Product.query.filter_by(category_id=product.category_id, is_active=True)
        .filter(Product.id != product.id)
        .limit(4)
        .all()
    )
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = (
            WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
            is not None
        )
    return render_template(
        "products/detail.html", product=product, related=related, in_wishlist=in_wishlist
    )


@main_bp.route("/account")
@login_required
def account():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template("account.html", addresses=addresses)


@main_bp.route("/account/addresses/add", methods=["POST"])
@login_required
def add_address():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address_line = request.form.get("address_line", "").strip()
    city = request.form.get("city", "").strip()
    make_default = bool(request.form.get("is_default"))

    if not all([full_name, phone, address_line, city]):
        flash("Please fill in every address field.", "error")
        return redirect(request.referrer or url_for("main.account"))

    if make_default:
        Address.query.filter_by(user_id=current_user.id).update({"is_default": False})

    address = Address(
        user_id=current_user.id,
        full_name=full_name,
        phone=phone,
        address_line=address_line,
        city=city,
        is_default=make_default or Address.query.filter_by(user_id=current_user.id).count() == 0,
    )
    db.session.add(address)
    db.session.commit()
    flash("Address saved.", "success")
    return redirect(request.referrer or url_for("main.account"))


@main_bp.route("/account/addresses/<int:address_id>/delete", methods=["POST"])
@login_required
def delete_address(address_id):
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    db.session.delete(address)
    db.session.commit()
    flash("Address removed.", "info")
    return redirect(url_for("main.account"))


@main_bp.route("/account/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        error = None
        if not name or not email:
            error = "Please fill in both your name and email."
        elif User.query.filter(User.email == email, User.id != current_user.id).first():
            error = "That email is already in use by another account."

        if error:
            flash(error, "error")
            return render_template("account_edit.html", name=name, email=email)

        current_user.name = name
        current_user.email = email
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("main.account"))

    return render_template("account_edit.html", name=current_user.name, email=current_user.email)


@main_bp.route("/account/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None
        if not current_user.check_password(current_password):
            error = "Your current password is incorrect."
        elif len(new_password) < 6:
            error = "New password must be at least 6 characters."
        elif new_password != confirm_password:
            error = "New passwords do not match."

        if error:
            flash(error, "error")
            return render_template("change_password.html")

        current_user.set_password(new_password)
        db.session.commit()
        flash("Your password has been changed.", "success")
        return redirect(url_for("main.account"))

    return render_template("change_password.html")
