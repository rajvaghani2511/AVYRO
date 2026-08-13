from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Cart, CartItem

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists.', 'warning')
            return render_template('auth/register.html')

        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Welcome to AVYRO! Account created successfully.', 'success')

        # Merge Guest Cart if exists
        guest_session_id = session.get('cart_session_id')
        if guest_session_id:
            guest_cart = Cart.query.filter_by(session_id=guest_session_id).first()
            if guest_cart:
                user_cart = Cart.query.filter_by(user_id=user.id).first()
                if not user_cart:
                    guest_cart.user_id = user.id
                    guest_cart.session_id = None
                else:
                    for g_item in guest_cart.items:
                        u_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=g_item.product_id).first()
                        if u_item:
                            u_item.quantity += g_item.quantity
                        else:
                            new_item = CartItem(cart_id=user_cart.id, product_id=g_item.product_id, quantity=g_item.quantity)
                            db.session.add(new_item)
                    db.session.delete(guest_cart)
                db.session.commit()

        next_page = request.args.get('next')
        return redirect(next_page or url_for('shop.home'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.name}!', 'success')

        # Merge Guest Cart if exists
        guest_session_id = session.get('cart_session_id')
        if guest_session_id:
            guest_cart = Cart.query.filter_by(session_id=guest_session_id).first()
            if guest_cart:
                user_cart = Cart.query.filter_by(user_id=user.id).first()
                if not user_cart:
                    guest_cart.user_id = user.id
                    guest_cart.session_id = None
                else:
                    for g_item in guest_cart.items:
                        u_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=g_item.product_id).first()
                        if u_item:
                            u_item.quantity += g_item.quantity
                        else:
                            new_item = CartItem(cart_id=user_cart.id, product_id=g_item.product_id, quantity=g_item.quantity)
                            db.session.add(new_item)
                    db.session.delete(guest_cart)
                db.session.commit()

        next_page = request.args.get('next')
        if user.is_admin and not next_page:
            return redirect(url_for('admin.dashboard'))
        return redirect(next_page or url_for('shop.home'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('shop.home'))
