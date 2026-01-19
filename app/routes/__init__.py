from .auth import auth_routes
from .cart import cart_routes
from .products import product_routes
from .profile import profile_routes
from .orders import order_routes
from .admin import admin_routes
from .contact import contact_routes
from .misc import misc_routes




def register_routes(app):
    auth_routes(app)
    cart_routes(app)
    product_routes(app)
    profile_routes(app)
    order_routes(app)
    admin_routes(app)
    contact_routes(app)
    misc_routes(app)
