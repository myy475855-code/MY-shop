from flask import render_template, request, redirect,url_for
from flask_login import current_user, login_required
from app import db
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Product, Comment

def product_routes(app):

    @app.route("/")
    def index():
        products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
        return render_template("index.html", products=products, user=current_user)

    @app.route("/products")
    def products():
        return render_template("products.html",
            products=Product.query.order_by(Product.created_at.desc()).all())

    @app.route("/product/<int:product_id>", methods=["GET","POST"])
    def product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            comment = Comment(
                product_id=product.id,
                user_id=current_user.id if current_user.is_authenticated else None,
                name=current_user.first_name if current_user.is_authenticated else "Guest",
                content=request.form.get("comment")
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(request.url)
        return render_template("product_detail.html", product=product)

    @app.route("/search")
    def search():
        q = request.args.get("q","")
        products = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%")) |
            (Product.categories.ilike(f"%{q}%"))
        ).all()
        return render_template("search_results.html", products=products, query=q)
    
    @app.route("/upload-product", methods=["GET", "POST"])
    @login_required
    def upload_product():
        # Only admin can upload
        if current_user.email != "myy502388@gmail.com":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))

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