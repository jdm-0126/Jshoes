from models import db
from models.delivery import Delivery, DeliveryItem
from models.product import Product
from sqlalchemy import func
from datetime import datetime, timedelta

def get_delivery_analytics(period='weekly'):
    today = datetime.utcnow().date()
    
    if period == 'daily':
        start_date = today
        end_date = today + timedelta(days=1)
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
    
    # Get delivered items summary
    delivered_items = db.session.query(
        Product.name,
        Product.category,
        func.sum(DeliveryItem.quantity).label('total_quantity')
    ).join(DeliveryItem).join(Delivery).filter(
        Delivery.delivered_at >= start_date,
        Delivery.delivered_at < end_date,
        Delivery.status == 'delivered'
    ).group_by(Product.id).all()
    
    # Get daily delivery counts
    daily_deliveries = db.session.query(
        func.date(Delivery.delivered_at).label('date'),
        func.count(Delivery.id).label('count')
    ).filter(
        Delivery.delivered_at >= start_date,
        Delivery.delivered_at < end_date,
        Delivery.status == 'delivered'
    ).group_by(func.date(Delivery.delivered_at)).all()
    
    return {
        'delivered_items': delivered_items,
        'daily_deliveries': daily_deliveries,
        'period': period
    }