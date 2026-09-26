"""
Seed MYY SHOP with demo data.

Run with:
    flask seed
or:
    python seed.py
"""

from app import create_app, db
from app.models import User, Category, Product, Review


DEMO_CATEGORIES = ["Mobile Phones", "Laptops", "Audio", "Home Appliances", "Fashion"]

DEMO_PRODUCTS = [
    dict(name="Samsung Galaxy A25", category="Mobile Phones", price=74999, sale_price=69999, stock=17,
         description="6.5-inch AMOLED display, 128GB storage, triple camera setup."),
    dict(name="iPhone 13", category="Mobile Phones", price=189999, sale_price=None, stock=6,
         description="6.1-inch Super Retina XDR display, A15 Bionic chip."),
    dict(name="Dell Inspiron 15", category="Laptops", price=145000, sale_price=132000, stock=9,
         description="15.6-inch FHD, Intel Core i5, 8GB RAM, 512GB SSD."),
    dict(name="MacBook Air M2", category="Laptops", price=289999, sale_price=None, stock=4,
         description="13.6-inch Liquid Retina display, Apple M2 chip, 8GB RAM."),
    dict(name="JBL Flip 6 Speaker", category="Audio", price=24999, sale_price=19999, stock=25,
         description="Portable waterproof Bluetooth speaker with punchy bass."),
    dict(name="Sony WH-1000XM4 Headphones", category="Audio", price=64999, sale_price=None, stock=3,
         description="Industry-leading noise cancellation, 30-hour battery life."),
    dict(name="Dawlance Microwave Oven 30L", category="Home Appliances", price=32999, sale_price=28999, stock=12,
         description="30-litre capacity with grill function and digital display."),
    dict(name="Haier Inverter AC 1.5 Ton", category="Home Appliances", price=189999, sale_price=None, stock=0,
         description="Energy-efficient inverter air conditioner with fast cooling."),
    dict(name="Men's Classic Leather Jacket", category="Fashion", price=12999, sale_price=9999, stock=20,
         description="Genuine leather jacket, available in black and brown."),
    dict(name="Women's Casual Sneakers", category="Fashion", price=6999, sale_price=None, stock=30,
         description="Lightweight everyday sneakers with breathable mesh upper."),
]


def run_seed():
    db.create_all()

    categories = {}
    for name in DEMO_CATEGORIES:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name)
            db.session.add(cat)
        categories[name] = cat
    db.session.flush()

    for item in DEMO_PRODUCTS:
        if Product.query.filter_by(name=item["name"]).first():
            continue
        product = Product(
            name=item["name"],
            price=item["price"],
            sale_price=item["sale_price"],
            stock=item["stock"],
            description=item["description"],
            category=categories[item["category"]],
        )
        db.session.add(product)

    if not User.query.filter_by(email="admin@myyshop.com").first():
        admin = User(name="Store Admin", email="admin@myyshop.com", is_admin=True)
        admin.set_password("Admin@123")
        db.session.add(admin)

    if not User.query.filter_by(email="demo.customer@myyshop.com").first():
        demo_customer = User(name="Sana Tariq", email="demo.customer@myyshop.com")
        demo_customer.set_password("Demo@1234")
        db.session.add(demo_customer)

    db.session.commit()

    # A few demo reviews so the ratings/reviews UI has something to show right away.
    demo_customer = User.query.filter_by(email="demo.customer@myyshop.com").first()
    admin = User.query.filter_by(email="admin@myyshop.com").first()
    demo_reviews = [
        ("Samsung Galaxy A25", demo_customer, 5, "Great value for the price, camera is surprisingly good."),
        ("Samsung Galaxy A25", admin, 4, "Solid daily driver. Battery easily lasts a full day."),
        ("JBL Flip 6 Speaker", demo_customer, 5, "Loud, clear, and the battery life is excellent."),
        ("Dell Inspiron 15", demo_customer, 3, "Does the job but gets a bit warm under load."),
        ("MacBook Air M2", admin, 5, "Silent, fast, and the battery life is genuinely all-day."),
    ]
    for product_name, user, rating, comment in demo_reviews:
        product = Product.query.filter_by(name=product_name).first()
        if not product or not user:
            continue
        if Review.query.filter_by(product_id=product.id, user_id=user.id).first():
            continue
        db.session.add(Review(product_id=product.id, user_id=user.id, rating=rating, comment=comment))

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_seed()
        print("Seeded MYY SHOP with demo categories, products, reviews, and two accounts.")
        print("Admin login    -> email: admin@myyshop.com        password: Admin@123")
        print("Customer login -> email: demo.customer@myyshop.com password: Demo@1234")
