from models import db
from models.product import Product
from models.inventory_alert import InventoryAlert
from datetime import datetime, timedelta

def check_low_stock():
    """Check for products with low stock and return alerts"""
    low_stock_products = []
    
    # Get all products with their alert settings
    products = db.session.query(Product, InventoryAlert).outerjoin(
        InventoryAlert, Product.id == InventoryAlert.product_id
    ).all()
    
    for product, alert in products:
        threshold = alert.alert_threshold if alert else 5  # Default threshold
        
        if product.stock <= threshold:
            # Check if alert was sent recently (within 24 hours)
            should_alert = True
            if alert and alert.last_alert_sent:
                time_since_alert = datetime.utcnow() - alert.last_alert_sent
                should_alert = time_since_alert > timedelta(hours=24)
            
            if should_alert:
                low_stock_products.append({
                    'product': product,
                    'current_stock': product.stock,
                    'threshold': threshold,
                    'alert_id': alert.id if alert else None
                })
    
    return low_stock_products

def update_alert_sent(alert_id):
    """Update the last alert sent timestamp"""
    if alert_id:
        alert = InventoryAlert.query.get(alert_id)
        if alert:
            alert.last_alert_sent = datetime.utcnow()
            db.session.commit()

def get_inventory_dashboard():
    """Get inventory overview for admin dashboard"""
    total_products = Product.query.count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()
    low_stock = Product.query.filter(Product.stock <= 5, Product.stock > 0).count()
    
    return {
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'in_stock': total_products - out_of_stock - low_stock
    }