import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from models import db
from models.product import Product

def update_boot_images():
    app = create_app()
    with app.app_context():
        # Update Leather Boots image
        leather_boots = Product.query.filter_by(name='Leather Boots').first()
        if leather_boots:
            leather_boots.image_url = 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400'
            
        # Update Hiking Boots image  
        hiking_boots = Product.query.filter_by(name='Hiking Boots').first()
        if hiking_boots:
            hiking_boots.image_url = 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=400'
            
        db.session.commit()
        print("Updated boot images successfully!")

if __name__ == '__main__':
    update_boot_images()