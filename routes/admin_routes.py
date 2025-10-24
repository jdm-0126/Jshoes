from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from functools import wraps
from models.product import Product
from models.order import Order
from models.inquiry import Inquiry
from models import db
from utils.forms import ProductForm
from utils.analytics import get_sales_analytics, get_inquiry_analytics
from utils.error_logger import log_error
import os

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_viewer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin or (hasattr(current_user, 'is_viewer') and current_user.is_viewer)):
            flash('Admin or viewer access required')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_or_viewer_required
def dashboard():
    period = request.args.get('period', 'weekly')
    delivery_limit = int(request.args.get('delivery_limit', 5))
    recent_limit = int(request.args.get('recent_limit', 5))
    
    try:
        sales_data = get_sales_analytics(period=period)
        inquiry_data = get_inquiry_analytics()
        
        # Get delivery orders with counts
        delivery_query = Order.query.filter(Order.status.in_(['paid', 'in_transit', 'delivered'])).order_by(Order.created_at.desc())
        delivery_total = delivery_query.count()
        delivery_orders = delivery_query.limit(5).all()
        
        # Get recent orders with counts
        recent_query = Order.query.order_by(Order.created_at.desc())
        recent_total = recent_query.count()
        recent_orders = recent_query.limit(5).all()
        
        recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
        
        # Get inventory data
        from utils.inventory_service import get_inventory_dashboard, check_low_stock
        inventory_data = get_inventory_dashboard()
        low_stock_alerts = check_low_stock()
    except Exception as e:
        print(f"Dashboard error: {e}")
        sales_data = {'total_sales': 0, 'avg_daily': 0, 'total_orders': 0, 'period': period}
        inquiry_data = {'new_inquiries': 0, 'total_inquiries': 0}
        delivery_orders = []
        recent_orders = []
        recent_inquiries = []
        inventory_data = {'total_products': 0, 'out_of_stock': 0, 'low_stock': 0, 'in_stock': 0}
        low_stock_alerts = []
        delivery_total = 0
        recent_total = 0
    
    # Hide sensitive data from viewers
    if hasattr(current_user, 'is_viewer') and current_user.is_viewer:
        sales_data = None
        inquiry_data = None
        delivery_orders = []
        recent_orders = []
        recent_inquiries = []
    
    return render_template('dashboard.html', 
                         sales_data=sales_data,
                         inquiry_data=inquiry_data,
                         delivery_orders=delivery_orders,
                         recent_orders=recent_orders,
                         recent_inquiries=recent_inquiries,
                         inventory_data=inventory_data,
                         low_stock_alerts=low_stock_alerts,
                         selected_period=period,
                         delivery_limit=delivery_limit,
                         recent_limit=recent_limit,
                         delivery_total=delivery_total,
                         recent_total=recent_total)

@admin.route('/products')
@login_required
@admin_or_viewer_required
def manage_products():
    category = request.args.get('category')
    brand = request.args.get('brand')
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if brand:
        query = query.filter_by(brand=brand)
    
    products = query.all()
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
    categories = [cat[0] for cat in categories]
    
    # Get brands for the selected category or all brands
    brand_query = db.session.query(Product.brand).distinct().filter(Product.brand.isnot(None))
    if category:
        brand_query = brand_query.filter_by(category=category)
    brands = [brand[0] for brand in brand_query.all()]
    
    return render_template('admin_products.html', products=products, categories=categories, brands=brands, selected_category=category, selected_brand=brand)

@admin.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_or_viewer_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            brand=form.brand.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            image_url=form.image_url.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('admin.manage_products'))
    return render_template('add_product.html', form=form)

@admin.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_or_viewer_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.brand = form.brand.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        product.image_url = form.image_url.data
        
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.manage_products'))
    
    return render_template('edit_product.html', form=form, product=product)

@admin.route('/orders')
@login_required
@admin_required
def manage_orders():
    from datetime import datetime, timedelta
    
    status_filter = request.args.get('status')
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    payment_method = request.args.get('payment_method')
    location = request.args.get('location', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = Order.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        from models.user import User
        query = query.join(User).filter(
            db.or_(
                Order.id.like(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Order.created_at >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Order.created_at < end)
        except ValueError:
            pass
    
    if payment_method:
        query = query.filter_by(payment_method=payment_method)
    
    if location:
        from models.user import User
        if not search:  # Only join User if not already joined
            query = query.join(User)
        query = query.filter(User.city.ilike(f'%{location}%'))
    
    # Apply sorting
    if sort_by == 'total_amount':
        sort_column = Order.total_amount
    elif sort_by == 'id':
        sort_column = Order.id
    else:
        sort_column = Order.created_at
    
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    orders = query.all()
    return render_template('admin_orders.html', orders=orders, selected_status=status_filter, search=search, start_date=start_date, end_date=end_date, payment_method=payment_method, location=location, sort_by=sort_by, sort_order=sort_order)

@admin.route('/user_delivery/<int:user_id>')
@login_required
@admin_required
def user_delivery(user_id):
    from models.user import User
    user = User.query.get_or_404(user_id)
    user_orders = Order.query.filter_by(user_id=user_id).filter(Order.status.in_(['paid', 'in_transit', 'delivered'])).order_by(Order.created_at.desc()).all()
    return render_template('user_delivery.html', user=user, orders=user_orders)

@admin.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    new_status = data.get('status')
    
    print(f"Updating order {order_id} from {order.status} to {new_status}")
    
    if new_status in ['in_transit', 'delivered', 'received']:
        order.status = new_status
        db.session.commit()
        print(f"Order {order_id} updated to {order.status}")
        return '', 200
    else:
        print(f"Invalid status: {new_status}")
        return '', 400

@admin.route('/contact_settings', methods=['GET', 'POST'])
@login_required
@admin_or_viewer_required
def contact_settings():
    from models.contact_settings import ContactSettings
    try:
        settings = ContactSettings.get_settings()
    except Exception as e:
        print(f"Contact settings error: {e}")
        # Create default settings if there's an error
        settings = ContactSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            settings.phone = request.form.get('phone')
            settings.email = request.form.get('email')
            settings.address = request.form.get('address')
            settings.business_hours = request.form.get('business_hours')
            settings.facebook_url = request.form.get('facebook_url')
            settings.instagram_url = request.form.get('instagram_url')
            # Testimonials are now static properties, no need to update
            
            db.session.commit()
            flash('Contact settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'error')
        return redirect(url_for('admin.contact_settings'))
    
    return render_template('contact_settings.html', settings=settings)

@admin.route('/inquiries')
@login_required
@admin_required
def manage_inquiries():
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template('admin_inquiries.html', inquiries=inquiries)

@admin.route('/inquiry/<int:id>')
@login_required
@admin_required
def view_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    return render_template('view_inquiry.html', inquiry=inquiry)

@admin.route('/update_inquiry_status/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_inquiry_status(id):
    inquiry = Inquiry.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['new', 'in_progress', 'resolved']:
        inquiry.status = new_status
        db.session.commit()
        return '', 200
    else:
        return '', 400

@admin.route('/download_errors')
@login_required
@admin_required
def download_errors():
    error_log_path = 'logs/errors.log'
    if os.path.exists(error_log_path):
        return send_file(error_log_path, as_attachment=True, download_name='jshoes_errors.log')
    else:
        flash('No error log file found', 'error')
        return redirect(url_for('admin.dashboard'))