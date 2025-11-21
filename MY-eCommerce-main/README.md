# MY-eCommerce
my eCommerce app built in python flask

Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.0.3
itsdangerous==2.1.2
python-dotenv==1.0.0
Werkzeug==2.3.7

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your_app_specific_password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=yourgmail@gmail.com

myshop/
│
├── app/
├─ requirements.txt
├─ static/
│  ├─ uploads/            # product images will be stored here
│  └─ css/, js/, images/  # your static files (bootstrap, icons)
└─ templates/
   ├─ base.html
   ├─ index.html
   ├─ login.html
   ├─ register.html
   ├─ profile.html
   ├─ upload_product.html
   ├─ product.html
   ├─ cart.html
   ├─ orders.html
   ├─ order_confirmation.html
   ├─ forgot_password.html
   └─ reset_link_sent.html


/upload-product
├── .env
├── run.py
└── requirements.txt




/upload-product
