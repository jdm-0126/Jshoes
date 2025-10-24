from models import db
from models.order import Order
from models.inquiry import Inquiry
from sqlalchemy import func
from datetime import datetime, timedelta

def get_sales_analytics(start_date=None, end_date=None, period='all'):
    today = datetime.utcnow().date()
    
    # Set date ranges based on period
    if period == 'daily':
        start_date = today
        end_date = today + timedelta(days=1)
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
    elif period == 'yearly':
        start_date = today - timedelta(days=365)
        end_date = today + timedelta(days=1)
    
    # Base query
    query = db.session.query(func.sum(Order.total_amount))
    order_query = Order.query
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Order.created_at >= start_date)
        order_query = order_query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at < end_date)
        order_query = order_query.filter(Order.created_at < end_date)
    
    total_sales = query.scalar() or 0
    total_orders = order_query.count()
    
    # Calculate averages
    if period == 'daily':
        avg_daily = total_sales
    elif period == 'weekly':
        avg_daily = total_sales / 7 if total_sales > 0 else 0
    elif period == 'monthly':
        avg_daily = total_sales / 30 if total_sales > 0 else 0
    elif period == 'yearly':
        avg_daily = total_sales / 365 if total_sales > 0 else 0
    else:
        # For 'all' period, calculate based on days since first order
        first_order = Order.query.order_by(Order.created_at.asc()).first()
        if first_order:
            days_active = (today - first_order.created_at.date()).days + 1
            avg_daily = total_sales / days_active if days_active > 0 else 0
        else:
            avg_daily = 0
    
    return {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_daily': avg_daily,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    }

def get_inquiry_analytics():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    total_inquiries = Inquiry.query.count()
    new_inquiries = Inquiry.query.filter_by(status='new').count()
    weekly_inquiries = Inquiry.query.filter(Inquiry.created_at >= week_ago).count()
    
    return {
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'weekly_inquiries': weekly_inquiries
    }