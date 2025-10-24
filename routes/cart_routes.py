# ...existing code...
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.product import Product
from models.order import Order, OrderItem
from models import db
from utils.email_service import send_order_confirmation
from models.cart import Cart, CartItem
from types import SimpleNamespace
from utils.error_logger import log_error

cart = Blueprint('cart', __name__)

@cart.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if current_user.is_authenticated:
        # For authenticated users, use database cart
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart_obj:
            cart_obj = Cart(user_id=current_user.id)
            db.session.add(cart_obj)
            db.session.flush()
        
        # Check if item already exists
        existing_item = CartItem.query.filter_by(cart_id=cart_obj.id, product_id=product_id).first()
        if existing_item:
            existing_item.quantity += 1
        else:
            product = Product.query.get(product_id)
            if product:
                new_item = CartItem(cart_id=cart_obj.id, product_id=product_id, quantity=1, price=product.price)
                db.session.add(new_item)
        
        db.session.commit()
        cart_count = sum(item.quantity for item in cart_obj.items)
    else:
        # For anonymous users, use session cart
        if 'cart' not in session:
            session['cart'] = {}
        cart_items = session['cart']
        product_id_str = str(product_id)
        if product_id_str in cart_items:
            cart_items[product_id_str] += 1
        else:
            cart_items[product_id_str] = 1
        session['cart'] = cart_items
        cart_count = sum(cart_items.values())
    
    return jsonify({'success': True, 'cart_count': cart_count})

@cart.route('/cart')
def view_cart():
    if current_user.is_authenticated:
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        items = cart_obj.items if cart_obj else []
        total = sum(item.price * item.quantity for item in items)
    else:
        session_cart = session.get('cart', {})
        items = []
        total = 0
        for pid_str, qty in session_cart.items():
            try:
                pid = int(pid_str)
            except ValueError:
                continue
            product = Product.query.get(pid)
            if not product:
                continue
            subtotal = product.price * qty
            total += subtotal
            item = SimpleNamespace()
            item.id = None
            item.product = product
            item.price = product.price
            item.quantity = qty
            items.append(item)
    return render_template('cart.html', products=items, total=total)

@cart.route('/checkout')
@login_required
def checkout():
    # Prefer DB cart for logged-in users, fallback to session cart
    items_to_checkout = []
    total = 0
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if cart_obj and cart_obj.items:
        for ci in cart_obj.items:
            prod = Product.query.get(ci.product_id)
            if not prod:
                continue
            # Check stock availability
            if prod.stock < ci.quantity:
                from flask import flash
                flash(f'Insufficient stock for {prod.name}. Available: {prod.stock}, Requested: {ci.quantity}', 'error')
                return redirect(url_for('cart.view_cart'))
            items_to_checkout.append((prod, ci.quantity, ci.price))
    else:
        session_cart = session.get('cart', {})
        for pid_str, qty in session_cart.items():
            try:
                pid = int(pid_str)
            except ValueError:
                continue
            prod = Product.query.get(pid)
            if not prod:
                continue
            # Check stock availability
            if prod.stock < qty:
                from flask import flash
                flash(f'Insufficient stock for {prod.name}. Available: {prod.stock}, Requested: {qty}', 'error')
                return redirect(url_for('cart.view_cart'))
            items_to_checkout.append((prod, qty, prod.price))

    if not items_to_checkout:
        return redirect(url_for('cart.view_cart'))

    order = Order(user_id=current_user.id, total_amount=0)
    db.session.add(order)
    db.session.flush()

    for prod, qty, price in items_to_checkout:
        subtotal = price * qty
        total += subtotal
        order_item = OrderItem(
            order_id=order.id,
            product_id=prod.id,
            quantity=qty,
            price=price
        )
        db.session.add(order_item)

    order.total_amount = total
    db.session.commit()

    # Don't clear cart here - only clear after successful payment
    send_order_confirmation(order)
    return redirect(url_for('payment.payment_page', order_id=order.id))

@cart.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    # if logged in, treat item_id as CartItem.id and remove from DB cart
    if current_user.is_authenticated:
        item = CartItem.query.get_or_404(item_id)
        if item.cart is None or item.cart.user_id != current_user.id:
            return jsonify(success=False, error='Unauthorized'), 403
        try:
            db.session.delete(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 400
        # recompute total from DB
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        total = sum(i.price * i.quantity for i in (cart_obj.items if cart_obj else []))
        cart_count = sum(i.quantity for i in (cart_obj.items if cart_obj else []))
        return jsonify(success=True, total=total, cart_count=cart_count)
    # anonymous user: treat item_id as product_id and remove from session cart
    session_cart = session.get('cart', {})
    pid = str(item_id)
    if pid in session_cart:
        session_cart.pop(pid, None)
        session['cart'] = session_cart
    # recompute total using remaining session items
    total = 0
    for pid_str, qty in session.get('cart', {}).items():
        prod = Product.query.get(int(pid_str))
        if prod:
            total += prod.price * qty
    return jsonify(success=True, total=total, cart_count=sum(session.get('cart', {}).values()))

@cart.route('/cart/clear', methods=['POST'])
def clear_cart():
    if current_user.is_authenticated:
        try:
            cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
            if cart_obj:
                CartItem.query.filter_by(cart_id=cart_obj.id).delete()
            db.session.commit()
            return jsonify(success=True, total=0, cart_count=0)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 400
    else:
        # anonymous: clear session cart
        session.pop('cart', None)
        return jsonify(success=True, total=0, cart_count=0)

@cart.route('/cart/count')
def cart_count():
    if current_user.is_authenticated:
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        count = sum(item.quantity for item in cart_obj.items) if cart_obj else 0
    else:
        count = sum(session.get('cart', {}).values())
    return jsonify(cart_count=count)

@cart.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart_quantity(item_id):
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    
    if current_user.is_authenticated:
        item = CartItem.query.get_or_404(item_id)
        if item.cart is None or item.cart.user_id != current_user.id:
            return jsonify(success=False, error='Unauthorized'), 403
        
        item.quantity = quantity
        db.session.commit()
        
        cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
        total = sum(i.price * i.quantity for i in (cart_obj.items if cart_obj else []))
        cart_count = sum(i.quantity for i in (cart_obj.items if cart_obj else []))
        return jsonify(success=True, total=total, cart_count=cart_count)
    else:
        # For session cart, treat item_id as product_id
        session_cart = session.get('cart', {})
        pid = str(item_id)
        if pid in session_cart:
            session_cart[pid] = quantity
            session['cart'] = session_cart
        
        # Recalculate total
        total = 0
        for pid_str, qty in session_cart.items():
            prod = Product.query.get(int(pid_str))
            if prod:
                total += prod.price * qty
        
        return jsonify(success=True, total=total, cart_count=sum(session_cart.values()))