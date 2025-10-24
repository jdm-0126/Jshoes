from app import create_app
from models import db
from models.product import Product

app = create_app()

with app.app_context():
    p = Product(name="Test Sneaker", description="Test", price=1999.00, stock=10, category="sneakers")
    db.session.add(p)
    db.session.commit()
    print("Inserted product id:", p.id)