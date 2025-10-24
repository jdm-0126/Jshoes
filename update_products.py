import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from models import db
from models.product import Product

def update_real_products():
    app = create_app()
    with app.app_context():
        # Clear existing products
        Product.query.delete()
        
        # Real JShoes products
        real_products = [
            {
                'name': 'Nike Air Force 1',
                'description': 'Classic white leather sneakers with iconic design. Perfect for everyday wear.',
                'price': 4500.00,
                'stock': 25,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400'
            },
            {
                'name': 'Adidas Ultraboost 22',
                'description': 'Premium running shoes with boost technology for maximum comfort.',
                'price': 8500.00,
                'stock': 15,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'
            },
            {
                'name': 'Converse Chuck Taylor',
                'description': 'Timeless canvas high-top sneakers. Available in multiple colors.',
                'price': 3200.00,
                'stock': 30,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=400'
            },
            {
                'name': 'Vans Old Skool',
                'description': 'Skateboarding shoes with signature side stripe. Durable and stylish.',
                'price': 3800.00,
                'stock': 20,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400'
            },
            {
                'name': 'Timberland Boots',
                'description': 'Premium leather work boots. Waterproof and built to last.',
                'price': 7200.00,
                'stock': 12,
                'category': 'boots',
                'image_url': 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400'
            },
            {
                'name': 'Dr. Martens 1460',
                'description': 'Iconic leather boots with air-cushioned sole. Classic style.',
                'price': 8900.00,
                'stock': 18,
                'category': 'boots',
                'image_url': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=400'
            },
            {
                'name': 'Havaianas Flip Flops',
                'description': 'Comfortable rubber sandals perfect for beach and casual wear.',
                'price': 1200.00,
                'stock': 50,
                'category': 'sandals',
                'image_url': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400'
            },
            {
                'name': 'Birkenstock Arizona',
                'description': 'Premium cork footbed sandals with adjustable straps.',
                'price': 4800.00,
                'stock': 22,
                'category': 'sandals',
                'image_url': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400'
            }
        ]
        
        for product_data in real_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Updated with {len(real_products)} real JShoes products!")
        print("Prices are now in Philippine Peso (₱)")

if __name__ == '__main__':
    update_real_products()