# MYY SHOP

A Flask e-commerce starter: browse products, add to cart/wishlist, check out with
Cash on Delivery, track orders, and manage everything from a simple admin dashboard.

## Features in this build (Phase 1 MVP + account/security additions)

- **Accounts:** register, sign in/out, password hashing (Werkzeug), saved delivery addresses
- **Profile & security:** edit profile (name/email), change password, forgot/reset password by email (Flask-Mail), a picture CAPTCHA on registration/sign-in/forgot-password, and a strong-password policy (min 8 characters, upper/lowercase, number, symbol) with a live checklist while typing
- **Addresses:** full_name, phone, address line, city, province/state, and country (Pakistan provinces + a short country list by default — edit `app/locations.py` to change either list)
- **Catalog:** categories, product listing with search/filter/sort, product detail pages with up to 7 photos per product shown as a slider/gallery (admin uploads, first photo becomes the cover thumbnail used everywhere else)
- **Reviews & ratings:** signed-in customers can leave a 1–5 star rating with an optional comment on any product (one review per person, editable/deletable anytime); product pages show an average rating, a star breakdown bar chart, and the full review list; admins can moderate (delete) any review from the dashboard
- **AI shopping assistant:** a floating "Ask AI" chat widget on every page — aware of store policies (COD, shipping fee/threshold) and, on a product page, that specific product's price, stock, rating and description. Calls the Anthropic API server-side only; your API key stays in `.env` and is never exposed to the browser. Leave the key blank and the widget degrades gracefully with a friendly "not configured" message instead of erroring.
- **Shopping:** cart (add/update/remove, stock-aware), wishlist with "move to cart"
- **Checkout:** address selection, shipping calculation, Cash on Delivery order placement, automatic order-confirmation email
- **Orders:** order history, status tracker (Pending → Confirmed → Processing → Shipped → Delivered), cancel while pending
- **Admin dashboard:** sales/orders/customers/products at a glance, low-stock & out-of-stock alerts, product CRUD with image upload, category management, order status updates, customer list
- **Security basics:** CSRF protection (Flask-WTF), hashed passwords, admin-only routes, one-time-use expiring password-reset tokens
- **Responsive:** the whole storefront and admin panel adapt down to phone width, including a slide-out mobile navigation menu

This is intentionally the *foundation* phase from the original feature roadmap
(reviews, coupons, payment gateways, RBAC, returns/refunds, extra notification
channels, SEO, caching, etc. are not built yet) — see **"What's next"** below for how to keep going.

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
flask seed
```

This creates all tables and seeds demo categories, 10 demo products, a few sample reviews, and two accounts:

```
Admin account
email:    admin@myyshop.com
password: Admin@123

Demo customer account
email:    demo.customer@myyshop.com
password: Demo@1234
```

**Change or remove these accounts before deploying anywhere public.**

## 3. Email setup (password reset + order confirmations)

Flask-Mail is wired up but works fine without any configuration:

- **No `MAIL_USERNAME` set** (the default) → the app runs in "dev mode." Password reset
  links and order confirmation emails are logged to the console/terminal instead of
  actually being sent, so you can copy the reset link from the log and test the flow
  without a real mailbox.
- **To send real emails**, fill in `.env`:
  ```
  MAIL_SERVER=smtp.gmail.com
  MAIL_PORT=587
  MAIL_USE_TLS=true
  MAIL_USERNAME=your-address@gmail.com
  MAIL_PASSWORD=your-app-password
  MAIL_DEFAULT_SENDER=your-address@gmail.com
  ```
  For Gmail you'll need an **App Password** (not your normal password) — enable
  2-Step Verification on the Google account, then create one under
  Google Account → Security → App passwords.

## 4. AI assistant setup (optional)

The "Ask AI" chat widget in the bottom-right corner works out of the box in a
disabled state — it'll politely say it isn't configured yet. To turn it on:

```
ANTHROPIC_API_KEY=sk-ant-...your-key...
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
```

Get a key at [console.anthropic.com](https://console.anthropic.com). The key is only ever
read server-side (in `app/ai_assistant.py`) — it's never sent to the browser. The
assistant knows the store's shipping/COD policy always, and additionally knows the
specific product's name, price, stock, rating and description whenever the visitor
is on that product's page.

## 5. Run it

```bash
python run.py
```

Visit **http://localhost:5000** — the storefront is live.
Sign in with the admin account above, then visit **http://localhost:5000/admin**
for the dashboard (the "Admin" link also appears in the nav once you're signed in as an admin).

## 6. Project structure

```
myy_shop/
├── app/
│   ├── __init__.py         # app factory, extensions, blueprint registration
│   ├── models.py           # User, Category, Product, ProductImage, Review, Cart, Wishlist, Address, Order...
│   ├── captcha.py          # picture CAPTCHA — renders a distorted PNG code with Pillow
│   ├── password_policy.py  # shared strong-password validation
│   ├── locations.py        # Country / Province dropdown option lists for address forms
│   ├── email_utils.py      # password reset tokens + reset/order-confirmation emails
│   ├── ai_assistant.py     # server-side Anthropic API call for the "Ask AI" widget
│   ├── icons.py            # inline SVG icon set used throughout the templates
│   ├── routes/
│   │   ├── main.py         # home, shop, product detail, account, edit profile, change password, /ai/ask
│   │   ├── auth.py         # register, login, logout, forgot/reset password, /auth/captcha-image
│   │   ├── cart.py
│   │   ├── wishlist.py
│   │   ├── checkout.py     # also triggers the order confirmation email
│   │   ├── orders.py       # customer order history
│   │   └── admin.py        # dashboard, products (incl. photo gallery), categories, orders, customers, reviews
│   ├── templates/
│   └── static/
│       ├── css/style.css   # responsive layout, mobile nav, design tokens
│       └── uploads/        # product images land here
├── config.py
├── seed.py
├── run.py
└── requirements.txt
```

## 7. Making a user an admin manually

If you didn't use the seed script, promote any existing user from the Flask shell:

```bash
flask shell
```
```python
u = User.query.filter_by(email="you@example.com").first()
u.is_admin = True
db.session.commit()
```

## 8. What's next

This build maps to **Phase 1** of the original roadmap (Product + Category + Inventory).
Suggested order for the phases that follow, each layering onto this codebase:

| Phase | Adds |
|---|---|
| 2 | Coupons, product variants (size/color/storage), better wishlist (price-drop alerts) |
| 3 | Multi-step checkout polish, multiple shipping methods, guest cart |
| 4 | Real payment gateways (JazzCash/Easypaisa/card), invoices (PDF) |
| 5 | ~~Reviews & ratings~~ (done), returns/refunds workflow |
| 6 | Role-based admin (Super Admin/Product Manager/etc.), reports & charts |
| 7 | Email notifications for every order event, support tickets |
| 8 | SEO metadata/sitemap, Redis caching, rate limiting, production hardening |

Each phase is additive — new models, blueprints, and templates alongside what's
already here, so nothing in this MVP has to be thrown away.

## 9. Notes on security before going live

- Set a strong, random `SECRET_KEY` in `.env`
- Switch `DATABASE_URL` to Postgres/MySQL for production (SQLite is fine for local dev)
- Put this behind HTTPS and set `SESSION_COOKIE_SECURE = True`
- Add `Flask-Limiter` for login rate limiting before exposing this publicly
- Never commit your real `ANTHROPIC_API_KEY` — it only belongs in `.env` (already gitignored)
- Never commit `.env` or the `*.db` file (already covered by `.gitignore`)
