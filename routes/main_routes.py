from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.product import Product
from models.inquiry import Inquiry
from models.order import Order
from models import db
from utils.forms import InquiryForm
from utils.email_service import send_inquiry_notification

main = Blueprint('main', __name__)

@main.route('/')
def index():
    featured_products = Product.query.limit(6).all()
    return render_template('index.html', products=featured_products)

# main = Blueprint('main', __name__)

# @main.route('/')
# def index():
#     products = Product.query.all()
#     return render_template('product_list.html', products=products)

@main.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    brand = request.args.get('brand')
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if brand:
        query = query.filter_by(brand=brand)
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
    categories = [cat[0] for cat in categories]
    
    # Get brands for the selected category or all brands
    brand_query = db.session.query(Product.brand).distinct().filter(Product.brand.isnot(None))
    if category:
        brand_query = brand_query.filter_by(category=category)
    brands = [brand[0] for brand in brand_query.all()]
    
    return render_template('product_list.html', products=products, categories=categories, brands=brands, selected_category=category, selected_brand=brand)

@main.route('/product/<int:id>')
def product_detail(id):
    from models.review import Review
    from sqlalchemy import func
    product = Product.query.get_or_404(id)
    
    # Get reviews and rating stats
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(product_id=id).scalar() or 0
    review_count = len(reviews)
    
    # Check if current user can review (must have purchased)
    can_review = False
    if current_user.is_authenticated:
        from models.order import Order, OrderItem
        purchased = db.session.query(OrderItem).join(Order).filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == id,
            Order.status.in_(['paid', 'delivered', 'received'])
        ).first()
        
        # Check if user already reviewed
        existing_review = Review.query.filter_by(user_id=current_user.id, product_id=id).first()
        can_review = purchased and not existing_review
    
    return render_template('product_detail.html', product=product, reviews=reviews, 
                         avg_rating=round(avg_rating, 1), review_count=review_count, can_review=can_review)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    from models.contact_settings import ContactSettings
    settings = ContactSettings.get_settings()
    form = InquiryForm()
    
    if form.validate_on_submit():
        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(inquiry)
        db.session.commit()
        
        # Send email notification
        if send_inquiry_notification(inquiry):
            flash('Your inquiry has been sent successfully!')
        else:
            flash('Your inquiry was saved but email notification failed.')
            
        return render_template('contact.html', form=InquiryForm(), settings=settings, success=True)
    return render_template('contact.html', form=form, settings=settings)

@main.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=orders)

@main.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    from models.review import Review
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', '').strip()
    
    # Validate rating
    if rating < 1 or rating > 5:
        flash('Invalid rating', 'error')
        return redirect(url_for('main.product_detail', id=product_id))
    
    # Check if user purchased the product
    from models.order import Order, OrderItem
    purchased = db.session.query(OrderItem).join(Order).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == product_id,
        Order.status.in_(['paid', 'delivered', 'received'])
    ).first()
    
    if not purchased:
        flash('You can only review products you have purchased', 'error')
        return redirect(url_for('main.product_detail', id=product_id))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        flash('You have already reviewed this product', 'error')
        return redirect(url_for('main.product_detail', id=product_id))
    
    # Create review
    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('main.product_detail', id=product_id))

@main.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.order_history'))
    
    if order.status == 'pending_payment':
        order.status = 'cancelled'
        db.session.commit()
        flash('Order cancelled successfully', 'success')
    else:
        flash('Cannot cancel this order', 'error')
    
    return redirect(url_for('main.order_history'))

