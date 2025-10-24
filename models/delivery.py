from datetime import datetime
from . import db

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='delivered')  # delivered, failed, returned
    notes = db.Column(db.Text)
    
    order = db.relationship('Order', backref='delivery', lazy=True)

class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    delivery = db.relationship('Delivery', backref='items', lazy=True)
    product = db.relationship('Product', backref='delivery_items', lazy=True)