import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app.models import User, Category, Product, Order
    return {"db": db, "User": User, "Category": Category, "Product": Product, "Order": Order}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
