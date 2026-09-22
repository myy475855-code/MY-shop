# MYY SHOP

A Flask e-commerce starter: browse products, add to cart/wishlist, check out with
Cash on Delivery, track orders, and manage everything from a simple admin dashboard.

## Features in this build (Phase 1 MVP)

- **Accounts:** register, sign in/out, password hashing (Werkzeug), saved delivery addresses
- **Catalog:** categories, product listing with search/filter/sort, product detail pages
- **Shopping:** cart (add/update/remove, stock-aware), wishlist with "move to cart"
- **Checkout:** address selection, shipping calculation, Cash on Delivery order placement
- **Orders:** order history, status tracker (Pending → Confirmed → Processing → Shipped → Delivered), cancel while pending
- **Admin dashboard:** sales/orders/customers/products at a glance, low-stock & out-of-stock alerts, product CRUD with image upload, category management, order status updates, customer list
- **Security basics:** CSRF protection (Flask-WTF), hashed passwords, admin-only routes

This is intentionally the *foundation* phase from the original feature roadmap
(reviews, coupons, payment gateways, RBAC, returns/refunds, notifications, SEO,
caching, etc. are not built yet) — see **"What's next"** below for how to keep going.

## 1. Setup

```bash
cd myy_shop
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then edit .env and set a real SECRET_KEY
```

## 2. Initialize the database

```bash
export FLASK_APP=run.py          # Windows (PowerShell): $env:FLASK_APP="run.py"
```

**Change or remove this account before deploying anywhere public.**

## 3. Run it

```bash
python run.py
```

Visit **http://localhost:5000** — the storefront is live.

for the dashboard (the "Admin" link also appears in the nav once you're signed in as an admin).

## 4. Project structure

```
myy_shop/
├── app/
│   ├── __init__.py         # app factory, extensions, blueprint registration
│   ├── models.py           # User, Category, Product, Cart, Wishlist, Address, Order...
│   ├── routes/
│   │   ├── main.py         # home, shop, product detail, account/addresses
│   │   ├── auth.py         # register, login, logout
│   │   ├── cart.py
│   │   ├── wishlist.py
│   │   ├── checkout.py
│   │   ├── orders.py       # customer order history
│   │   └── admin.py        # dashboard, products, categories, orders, customers
│   ├── templates/
│   └── static/
│       ├── css/style.css
│       └── uploads/        # product images land here
├── config.py
├── run.py
└── requirements.txt
```

## 5. Making a user an admin manually

If you didn't use the seed script, promote any existing user from the Flask shell:

```bash
flask shell
```
```python
u = User.query.filter_by(email="you@example.com").first()
u.is_admin = True
db.session.commit()
```

## 6. What's next

This build maps to **Phase 1** of the original roadmap (Product + Category + Inventory).
Suggested order for the phases that follow, each layering onto this codebase:

| Phase | Adds |
|---|---|
| 2 | Coupons, product variants (size/color/storage), better wishlist (price-drop alerts) |
| 3 | Multi-step checkout polish, multiple shipping methods, guest cart |
| 4 | Real payment gateways (JazzCash/Easypaisa/card), invoices (PDF) |
| 5 | Reviews & ratings, returns/refunds workflow |
| 6 | Role-based admin (Super Admin/Product Manager/etc.), reports & charts |
| 7 | Email notifications for every order event, support tickets |
| 8 | SEO metadata/sitemap, Redis caching, rate limiting, production hardening |

Each phase is additive — new models, blueprints, and templates alongside what's
already here, so nothing in this MVP has to be thrown away.

## 7. Notes on security before going live

- Set a strong, random `SECRET_KEY` in `.env`
- Switch `DATABASE_URL` to Postgres/MySQL for production (SQLite is fine for local dev)
- Put this behind HTTPS and set `SESSION_COOKIE_SECURE = True`
- Add `Flask-Limiter` for login rate limiting before exposing this publicly
- Never commit `.env` or the `*.db` file (already covered by `.gitignore`)
