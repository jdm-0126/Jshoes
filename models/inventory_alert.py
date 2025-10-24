from datetime import datetime
from . import db

class InventoryAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    alert_threshold = db.Column(db.Integer, default=5)  # Alert when stock <= this
    is_active = db.Column(db.Boolean, default=True)
    last_alert_sent = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='inventory_alert', lazy=True)