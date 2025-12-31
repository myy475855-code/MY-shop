from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import db
from app.models import Product, Comment, Rating, Favorite
from app.routes.misc import admin_required


def product_routes(app):

    # ===================== HOME =====================
    @app.route("/")
    def index():
        products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
        return render_template("index.html", products=products, user=current_user)


    # ===================== PRODUCTS LIST =====================
    @app.route("/products")
    def products():
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template("products.html", products=products)


    # ===================== PRODUCT DETAIL =====================
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

        # Parse categories and specifications
        categories = product.categories.split(",") if product.categories else []
        specifications = product.specifications.split("\n") if product.specifications else []

        # Collect images safely
        images = [img for img in [product.main_image, product.image2, product.image3, product.image4] if img]

        # Get comments
        comments = Comment.query.filter_by(product_id=product.id).order_by(Comment.created_at.desc()).all()

        # Ratings and favorites
        avg_rating = db.session.query(func.avg(Rating.stars)).filter_by(product_id=product.id).scalar() or 0
        user_rating_obj = Rating.query.filter_by(user_id=current_user.id, product_id=product.id).first() if current_user.is_authenticated else None
        user_rating = user_rating_obj.stars if user_rating_obj else 0
        is_fav = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None if current_user.is_authenticated else False

        return render_template(
            "product_detail.html",
            product=product,
            images=images,
            categories=categories,
            specifications=specifications,
            comments=comments,
            avg_rating=round(avg_rating, 1),
            user_rating=user_rating,
            is_fav=is_fav
        )


    # ===================== SEARCH =====================
    @app.route("/search")
    def search():
        q = request.args.get("q", "")
        products = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%")) |
            (Product.categories.ilike(f"%{q}%"))
        ).all()
        return render_template("search_results.html", products=products, query=q)


    # ===================== UPLOAD PRODUCT (ADMIN) =====================
    @app.route("/upload-product", methods=["GET", "POST"])
    @login_required
    @admin_required
    def upload_product():
        if request.method == "POST":
            name = request.form.get("product_name")
            description = request.form.get("description")
            price = float(request.form.get("price") or 0)
            discount_price = request.form.get("discount_price")
            discount_price = float(discount_price) if discount_price else None

            # Categories
            categories = request.form.getlist("categories[]")
            categories = ",".join(categories)

            # Specifications
            spec_names = request.form.getlist("spec_name[]")
            spec_values = request.form.getlist("spec_value[]")
            specifications = "\n".join([f"{n}: {v}" for n, v in zip(spec_names, spec_values) if n and v])

            # Images
            images = [request.files.get(f"image{i}") for i in range(1, 5)]
            filenames = []
            for img in images:
                if img and img.filename != "":
                    filename = secure_filename(img.filename)
                    img.save(current_app.config["UPLOAD_FOLDER"] + "/" + filename)
                    filenames.append(filename)
                else:
                    filenames.append(None)

            # Create product
            product = Product(
                name=name,
                description=description,
                specifications=specifications,
                categories=categories,
                price=price,
                discount_price=discount_price,
                main_image=filenames[0],
                image2=filenames[1],
                image3=filenames[2],
                image4=filenames[3]
            )
            db.session.add(product)
            db.session.commit()
            flash("Product uploaded successfully!", "success")
            return redirect(url_for("upload_product"))

        return render_template("upload.html")


    # ===================== EDIT PRODUCT (ADMIN) =====================
    @app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)

        if request.method == "POST":
            product.name = request.form.get("product_name")
            product.description = request.form.get("description")
            product.price = float(request.form.get("price") or 0)
            discount_price = request.form.get("discount_price")
            product.discount_price = float(discount_price) if discount_price else None

            # Categories
            categories = request.form.getlist("categories[]")
            product.categories = ",".join(categories)

            # Specifications
            spec_names = request.form.getlist("spec_name[]")
            spec_values = request.form.getlist("spec_value[]")
            product.specifications = "\n".join([f"{n}: {v}" for n, v in zip(spec_names, spec_values) if n and v])

            # Images
            images = [request.files.get(f"image{i}") for i in range(1, 5)]
            image_fields = ["main_image", "image2", "image3", "image4"]
            for img, field in zip(images, image_fields):
                if img and img.filename:
                    filename = secure_filename(img.filename)
                    img.save(current_app.config["UPLOAD_FOLDER"] + "/" + filename)
                    setattr(product, field, filename)

            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("product_detail", product_id=product.id))

        return render_template("edit_product.html", product=product)


    # ===================== DELETE PRODUCT (ADMIN) =====================
    @app.route("/delete-product/<int:product_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully!", "success")
        return redirect(url_for("index"))


    # ===================== RATE PRODUCT =====================
    @app.route("/rate/<int:product_id>/<int:stars>")
    @login_required
    def rate_product(product_id, stars):
        stars = max(1, min(5, stars))
        rating = Rating.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if rating:
            rating.stars = stars
        else:
            db.session.add(Rating(user_id=current_user.id, product_id=product_id, stars=stars))
        db.session.commit()
        flash("Rating saved!", "success")
        return redirect(request.referrer)


    # ===================== FAVORITE PRODUCT =====================
    @app.route("/favorite/<int:product_id>")
    @login_required
    def toggle_favorite(product_id):
        fav = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if fav:
            db.session.delete(fav)
            flash("Removed from favorites", "warning")
        else:
            db.session.add(Favorite(user_id=current_user.id, product_id=product_id))
            flash("Added to favorites", "success")
        db.session.commit()
        return redirect(request.referrer)


    # ===================== FAVORITES PAGE =====================
    @app.route("/favorites")
    @login_required
    def favorites():
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        products = [f.product for f in favs]
        return render_template("favorites.html", products=products)
