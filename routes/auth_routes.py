from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models.user import User
from models.cart import Cart, CartItem
from models.product import Product
from models import db
from utils.forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Migrate session cart to database cart
            session_cart = session.get('cart', {})
            if session_cart:
                cart_obj = Cart.query.filter_by(user_id=user.id).first()
                if not cart_obj:
                    cart_obj = Cart(user_id=user.id)
                    db.session.add(cart_obj)
                    db.session.flush()
                
                for pid_str, qty in session_cart.items():
                    try:
                        pid = int(pid_str)
                        product = Product.query.get(pid)
                        if product:
                            existing_item = CartItem.query.filter_by(cart_id=cart_obj.id, product_id=pid).first()
                            if existing_item:
                                existing_item.quantity += qty
                            else:
                                new_item = CartItem(cart_id=cart_obj.id, product_id=pid, quantity=qty, price=product.price)
                                db.session.add(new_item)
                    except ValueError:
                        continue
                
                db.session.commit()
                session.pop('cart', None)  # Clear session cart
            
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))