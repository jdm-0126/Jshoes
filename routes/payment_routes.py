from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models.order import Order
from models import db
from utils.paymongo_service import PayMongoService

payment = Blueprint('payment', __name__)

@payment.route('/payment/<int:order_id>')
@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('main.index'))
    
    return render_template('payment.html', order=order)

@payment.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    # Check if PayMongo keys are configured
    if not current_app.config.get('PAYMONGO_SECRET_KEY'):
        return jsonify({'success': False, 'message': 'Payment system not configured'})
    
    # Map payment methods to valid PayMongo source types
    paymongo_types = {
        'gcash': 'gcash',
        'paymaya': 'paymaya', 
        'shopeepay': 'grab_pay',
        'qrph': 'gcash'  # Default QR PH to GCash
    }
    
    paymongo_type = paymongo_types.get(payment_method, 'gcash')
    
    try:
        # Create PayMongo payment source
        source_response = PayMongoService.create_source(
            amount=order.total_amount,
            type=paymongo_type
        )
        
        if 'error' in source_response:
            return jsonify({'success': False, 'message': source_response['error']})
        
        if 'data' in source_response:
            source_data = source_response['data']
            checkout_url = source_data['attributes']['redirect']['checkout_url']
            
            # Store source ID for tracking
            order.payment_source_id = source_data['id']
            order.payment_method = payment_method
            order.status = 'pending_payment'
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'checkout_url': checkout_url,
                'message': f'Redirecting to {payment_method.upper()} payment'
            })
        else:
            error_msg = 'Payment processing failed'
            if 'errors' in source_response:
                error_msg = source_response['errors'][0].get('detail', error_msg)
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        print(f"Payment error: {str(e)}")
        return jsonify({'success': False, 'message': f'Payment error: {str(e)}'})

@payment.route('/payment/success')
def payment_success():
    # Get the most recent order for this user
    if current_user.is_authenticated:
        from models.cart import Cart, CartItem
        from models.product import Product
        recent_order = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).first()
        
        # Deduct stock for paid order and send receipt
        if recent_order and recent_order.status == 'pending_payment':
            recent_order.status = 'paid'
            for item in recent_order.items:
                product = Product.query.get(item.product_id)
                if product and product.stock >= item.quantity:
                    product.stock -= item.quantity
            db.session.commit()
            
            # Send payment receipt email
            from utils.receipt_service import send_payment_receipt
            send_payment_receipt(recent_order)
        
        # Clear cart after successful payment
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        if cart_obj:
            CartItem.query.filter_by(cart_id=cart_obj.id).delete()
            db.session.commit()
        
        if recent_order:
            return redirect(url_for('payment.delivery_details', order_id=recent_order.id))
    else:
        from flask import session
        session.pop('cart', None)
    
    return render_template('payment_success.html')

@payment.route('/payment/failed')
def payment_failed():
    flash('Payment failed. Please try again or choose a different payment method.', 'error')
    return redirect(url_for('cart.view_cart'))

@payment.route('/delivery/<int:order_id>', methods=['GET', 'POST'])
@login_required
def delivery_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        from datetime import datetime
        delivery_date_str = request.form.get('delivery_date')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        
        # Update user delivery info
        current_user.phone = phone
        current_user.address = address
        current_user.city = city
        current_user.postal_code = postal_code
        
        # Update order delivery date
        if delivery_date_str:
            order.delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Delivery details saved successfully!', 'success')
        return redirect(url_for('payment.order_confirmation', order_id=order.id))
    
    return render_template('delivery_details.html', order=order, user=current_user)

@payment.route('/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('order_confirmation.html', order=order)