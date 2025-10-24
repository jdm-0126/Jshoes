from . import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Product {self.name}>'