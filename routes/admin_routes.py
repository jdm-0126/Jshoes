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
    
    try:
        sales_data = get_sales_analytics(period=period)
        inquiry_data = get_inquiry_analytics()
        delivery_orders = Order.query.filter(Order.status.in_(['paid', 'in_transit', 'delivered'])).order_by(Order.created_at.desc()).limit(5).all()
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
    except Exception as e:
        print(f"Dashboard error: {e}")
        sales_data = {'total_sales': 0, 'avg_daily': 0, 'total_orders': 0, 'period': period}
        inquiry_data = {'new_inquiries': 0, 'total_inquiries': 0}
        delivery_orders = []
        recent_orders = []
        recent_inquiries = []
    
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
                         selected_period=period)

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
    status_filter = request.args.get('status')
    query = Order.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders, selected_status=status_filter)

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
    settings = ContactSettings.get_settings()
    
    if request.method == 'POST':
        settings.phone = request.form.get('phone')
        settings.email = request.form.get('email')
        settings.address = request.form.get('address')
        settings.business_hours = request.form.get('business_hours')
        settings.facebook_url = request.form.get('facebook_url')
        settings.instagram_url = request.form.get('instagram_url')
        
        db.session.commit()
        flash('Contact settings updated successfully', 'success')
        return redirect(url_for('admin.contact_settings'))
    
    return render_template('contact_settings.html', settings=settings)

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