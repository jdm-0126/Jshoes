from app import create_app
from models.user import User
from models.order import Order, OrderItem
from models.product import Product
from models import db
from utils.receipt_service import send_payment_receipt
from datetime import datetime

# Create test order and send receipt
app = create_app()

with app.app_context():
    # Create test user if not exists
    test_user = User.query.filter_by(email='josephmaninang3@gmail.com').first()
    if not test_user:
        test_user = User(
            username='Test Customer',
            email='josephmaninang3@gmail.com'
        )
        test_user.set_password('test123')
        test_user.address = '123 Test Street'
        test_user.city = 'Test City'
        test_user.postal_code = '1234'
        db.session.add(test_user)
        db.session.commit()
    
    # Create test product if not exists
    test_product = Product.query.first()
    if not test_product:
        test_product = Product(
            name='Test Shoe',
            brand='Test Brand',
            description='Test shoe for email testing',
            price=1500.00,
            stock=10,
            category='sneakers'
        )
        db.session.add(test_product)
        db.session.commit()
    
    # Create test order
    test_order = Order(
        user_id=test_user.id,
        total_amount=1500.00,
        status='paid',
        payment_method='gcash',
        delivery_date=datetime.now().date()
    )
    db.session.add(test_order)
    db.session.flush()
    
    # Add order item
    order_item = OrderItem(
        order_id=test_order.id,
        product_id=test_product.id,
        quantity=1,
        price=1500.00
    )
    db.session.add(order_item)
    db.session.commit()
    
    # Send test receipt
    print("Sending test receipt email...")
    result = send_payment_receipt(test_order)
    
    if result:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
    
    # Clean up test data
    db.session.delete(order_item)
    db.session.delete(test_order)
    db.session.commit()
    print("Test data cleaned up")