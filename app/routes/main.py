from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Product, Category, Address, WishlistItem, User, Review
from app.password_policy import validate_password_strength
from app.locations import COUNTRIES, PAKISTAN_PROVINCES
from app.ai_assistant import ai_configured, build_system_prompt, ask_ai

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
    user_review = None
    if current_user.is_authenticated:
        in_wishlist = (
            WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
            is not None
        )
        user_review = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()

    reviews = (
        Review.query.filter_by(product_id=product.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "products/detail.html", product=product, related=related, in_wishlist=in_wishlist,
        reviews=reviews, user_review=user_review,
    )


@main_bp.route("/product/<slug>/review", methods=["POST"])
@login_required
def submit_review(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please choose a star rating.", "error")
        return redirect(url_for("main.product_detail", slug=slug) + "#reviews")

    existing = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
        existing.updated_at = datetime.utcnow()
        flash("Your review has been updated.", "success")
    else:
        db.session.add(Review(product_id=product.id, user_id=current_user.id, rating=rating, comment=comment))
        flash("Thanks for your review!", "success")

    db.session.commit()
    return redirect(url_for("main.product_detail", slug=slug) + "#reviews")


@main_bp.route("/product/<slug>/review/delete", methods=["POST"])
@login_required
def delete_review(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    review = Review.query.filter_by(product_id=product.id, user_id=current_user.id).first()
    if review:
        db.session.delete(review)
        db.session.commit()
        flash("Your review has been removed.", "info")
    return redirect(url_for("main.product_detail", slug=slug) + "#reviews")


@main_bp.route("/account")
@login_required
def account():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "account.html", addresses=addresses, countries=COUNTRIES, provinces=PAKISTAN_PROVINCES
    )


@main_bp.route("/welcome/address", methods=["GET", "POST"])
@login_required
def onboarding_address():
    """Shown right after registration — a delivery address is required before continuing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address_line = request.form.get("address_line", "").strip()
        city = request.form.get("city", "").strip()
        province = request.form.get("province", "").strip()
        country = request.form.get("country", "").strip()

        if not all([full_name, phone, address_line, city, province, country]):
            flash("Please fill in every field so we know where to deliver your orders.", "error")
            return render_template(
                "onboarding_address.html",
                full_name=full_name, phone=phone, address_line=address_line,
                city=city, province=province, country=country,
                countries=COUNTRIES, provinces=PAKISTAN_PROVINCES,
            )

        address = Address(
            user_id=current_user.id,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            province=province,
            country=country,
            is_default=True,
        )
        db.session.add(address)
        db.session.commit()
        flash("You're all set! Your delivery address has been saved.", "success")
        return redirect(url_for("main.home"))

    return render_template(
        "onboarding_address.html", full_name=current_user.name,
        countries=COUNTRIES, provinces=PAKISTAN_PROVINCES,
    )


@main_bp.route("/account/addresses/add", methods=["POST"])
@login_required
def add_address():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address_line = request.form.get("address_line", "").strip()
    city = request.form.get("city", "").strip()
    province = request.form.get("province", "").strip()
    country = request.form.get("country", "").strip()
    make_default = bool(request.form.get("is_default"))

    if not all([full_name, phone, address_line, city, province, country]):
        flash("Please fill in every address field, including province and country.", "error")
        return redirect(request.referrer or url_for("main.account"))

    if make_default:
        Address.query.filter_by(user_id=current_user.id).update({"is_default": False})

    address = Address(
        user_id=current_user.id,
        full_name=full_name,
        phone=phone,
        address_line=address_line,
        city=city,
        province=province,
        country=country,
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
        is_strong, strength_message = validate_password_strength(new_password)
        if not current_user.check_password(current_password):
            error = "Your current password is incorrect."
        elif not is_strong:
            error = strength_message
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


@main_bp.route("/ai/ask", methods=["POST"])
def ai_ask():
    if not ai_configured():
        return jsonify({
            "error": "The AI assistant isn't set up yet — add an ANTHROPIC_API_KEY in .env to enable it."
        }), 503

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    product_slug = data.get("product_slug")
    raw_history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Please type a question first."}), 400
    if len(user_message) > 500:
        return jsonify({"error": "That question is a bit long — please shorten it to under 500 characters."}), 400

    # Only trust well-formed turns, and cap how much history we forward.
    clean_history = []
    if isinstance(raw_history, list):
        for turn in raw_history[-8:]:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = str(turn.get("content", ""))[:1000]
            if role in ("user", "assistant") and content:
                clean_history.append({"role": role, "content": content})

    product = None
    if product_slug:
        product = Product.query.filter_by(slug=product_slug, is_active=True).first()

    system_prompt = build_system_prompt(product)
    messages = clean_history + [{"role": "user", "content": user_message}]

    try:
        answer = ask_ai(system_prompt, messages)
    except Exception:
        current_app.logger.exception("AI assistant request failed")
        return jsonify({
            "error": "Sorry, the assistant is having trouble right now. Please try again in a moment."
        }), 502

    return jsonify({"answer": answer})
