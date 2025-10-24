import os
os.environ['FLASK_ENV'] = 'production'  # Force MySQL

from app import create_app
from models import db
from models.product import Product

def seed_products():
    app = create_app()
    with app.app_context():
        # Check if products already exist
        if Product.query.count() > 0:
            print("Products already exist. Skipping seeding.")
            return
        
        sample_products = [
            {
                'name': 'Classic White Sneakers',
                'description': 'Comfortable white sneakers perfect for everyday wear. Made with premium materials.',
                'price': 89.99,
                'stock': 50,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400'
            },
            {
                'name': 'Leather Boots',
                'description': 'Durable leather boots for outdoor adventures and casual wear.',
                'price': 149.99,
                'stock': 30,
                'category': 'boots',
                'image_url': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400'
            },
            {
                'name': 'Summer Sandals',
                'description': 'Lightweight and comfortable sandals for summer days.',
                'price': 39.99,
                'stock': 75,
                'category': 'sandals',
                'image_url': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400'
            },
            {
                'name': 'Running Shoes',
                'description': 'High-performance running shoes with advanced cushioning technology.',
                'price': 129.99,
                'stock': 40,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'
            },
            {
                'name': 'Hiking Boots',
                'description': 'Waterproof hiking boots designed for rugged terrain.',
                'price': 199.99,
                'stock': 25,
                'category': 'boots',
                'image_url': 'https://images.unsplash.com/photo-1551107696-a4b57dc104cd?w=400'
            },
            {
                'name': 'Casual Loafers',
                'description': 'Elegant loafers perfect for business casual occasions.',
                'price': 79.99,
                'stock': 35,
                'category': 'sneakers',
                'image_url': 'https://images.unsplash.com/photo-1582897085656-c636d006a246?w=400'
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Successfully added {len(sample_products)} products to the database.")

if __name__ == '__main__':
    seed_products()