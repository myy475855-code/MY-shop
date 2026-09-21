"""
Seed MYY SHOP with demo data.

Run with:
    flask seed
or:
    python seed.py
"""

from app import create_app, db
from app.models import User, Category, Product


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
        admin.set_password("admin123")
        db.session.add(admin)

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_seed()
        print("Seeded MYY SHOP with demo categories, products, and an admin account.")
        print("Admin login -> email: admin@myyshop.com  password: admin123")
