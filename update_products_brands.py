from app import create_app
from models import db
from models.product import Product

app = create_app()

with app.app_context():
    # Add brand column
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE product ADD COLUMN brand VARCHAR(50)'))
            conn.commit()
        print("Added brand column to products table")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Brand column already exists")
        else:
            print(f"Error adding brand column: {e}")
    
    # Update existing products with brands and better categories
    products_data = [
        {"name": "Converse Chuck Taylor", "category": "sneakers", "brand": "Converse"},
        {"name": "Vans Old Skool", "category": "sneakers", "brand": "Vans"},
        {"name": "Timberland Boots", "category": "boots", "brand": "Timberland"},
        {"name": "Nike Air Force 1", "category": "sneakers", "brand": "Nike"},
        {"name": "Adidas Stan Smith", "category": "sneakers", "brand": "Adidas"},
        {"name": "Dr. Martens 1460", "category": "boots", "brand": "Dr. Martens"},
        {"name": "Puma Suede Classic", "category": "sneakers", "brand": "Puma"},
        {"name": "New Balance 574", "category": "running", "brand": "New Balance"},
        {"name": "Reebok Classic Leather", "category": "sneakers", "brand": "Reebok"}
    ]
    
    # Update existing products
    for product_data in products_data:
        product = Product.query.filter_by(name=product_data["name"]).first()
        if product:
            product.category = product_data["category"]
            product.brand = product_data["brand"]
            print(f"Updated {product.name} - {product_data['brand']} - {product_data['category']}")
    
    # Add new products if we have less than 9
    existing_count = Product.query.count()
    if existing_count < 9:
        new_products = [
            {"name": "Nike Air Max 90", "price": 5500, "category": "running", "brand": "Nike", "stock": 15},
            {"name": "Adidas Ultraboost", "price": 8500, "category": "running", "brand": "Adidas", "stock": 12},
            {"name": "Converse All Star High", "price": 3800, "category": "sneakers", "brand": "Converse", "stock": 20},
            {"name": "Vans Authentic", "price": 3200, "category": "sneakers", "brand": "Vans", "stock": 18},
            {"name": "Puma RS-X", "price": 6200, "category": "sneakers", "brand": "Puma", "stock": 10},
            {"name": "New Balance 990v5", "price": 9500, "category": "running", "brand": "New Balance", "stock": 8}
        ]
        
        for product_data in new_products[:(9-existing_count)]:
            new_product = Product(
                name=product_data["name"],
                price=product_data["price"],
                category=product_data["category"],
                brand=product_data["brand"],
                stock=product_data["stock"],
                description=f"Premium {product_data['brand']} {product_data['category']} shoes"
            )
            db.session.add(new_product)
            print(f"Added new product: {product_data['name']}")
    
    db.session.commit()
    print("Products updated successfully!")