from datetime import datetime
from . import db

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # quantity = db.Column(db.Integer, default=1)
     # product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cart {self.id} user={self.user_id}>'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')

    def __repr__(self):
        return f'<CartItem {self.id} product={self.product_id} qty={self.quantity}>'