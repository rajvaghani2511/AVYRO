import re
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Cart, CartItem, PhoneOTP
from app.utils_auth import get_google_auth_url, exchange_google_code_for_user

auth_bp = Blueprint('auth', __name__)

def merge_guest_cart_to_user(user):
    """Merges guest session cart with authenticated user cart."""
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
            session.pop('cart_session_id', None)


@auth_bp.route('/login', methods=['GET'], endpoint='login')
@auth_bp.route('/register', methods=['GET'], endpoint='register')
@auth_bp.route('/customer-login', methods=['GET'], endpoint='customer_auth')
def customer_auth():
    if current_user.is_authenticated:
        next_page = request.args.get('next') or session.get('oauth_next')
        if next_page:
            session.pop('oauth_next', None)
            return redirect(next_page)
        return redirect(url_for('account.account'))

    next_url = request.args.get('next', '')
    active_tab = 'register' if request.endpoint == 'auth.register' else 'login'
    return render_template('auth/customer_auth.html', next_url=next_url, active_tab=active_tab)


@auth_bp.route('/api/auth/phone/send-otp', methods=['POST'])
def send_phone_otp():
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    mode = data.get('mode', 'login') # 'login' or 'create_account'

    # Format phone and validate
    clean_digits = re.sub(r'[^0-9]', '', phone)
    if clean_digits.startswith('91') and len(clean_digits) == 12:
        clean_digits = clean_digits[2:]

    if len(clean_digits) != 10 or not re.match(r'^[6-9][0-9]{9}$', clean_digits):
        return jsonify({'success': False, 'message': 'Please enter a valid 10-digit Indian mobile number.'}), 400

    formatted_phone = f"+91 {clean_digits}"
    existing_user = User.query.filter_by(phone=formatted_phone).first()

    if mode == 'login' and not existing_user:
        return jsonify({'success': False, 'message': 'No account found with this mobile number. Please click Create Account.'}), 404

    if mode == 'create_account' and existing_user and existing_user.phone_verified:
        return jsonify({'success': False, 'message': 'An account already exists with this phone number. Please click Login.'}), 400

    success, msg, cooldown = PhoneOTP.generate_otp(formatted_phone)
    if success:
        return jsonify({'success': True, 'message': msg, 'cooldown': cooldown})
    else:
        return jsonify({'success': False, 'message': msg, 'cooldown': cooldown}), 400


@auth_bp.route('/api/auth/phone/verify-otp', methods=['POST'])
def verify_phone_otp():
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    otp = data.get('otp', '').strip()
    mode = data.get('mode', 'login')
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    next_url = data.get('next_url', '').strip()

    clean_digits = re.sub(r'[^0-9]', '', phone)
    if clean_digits.startswith('91') and len(clean_digits) == 12:
        clean_digits = clean_digits[2:]

    if len(clean_digits) != 10:
        return jsonify({'success': False, 'message': 'Please enter a valid 10-digit Indian mobile number.'}), 400

    formatted_phone = f"+91 {clean_digits}"

    verified, msg = PhoneOTP.verify_otp(formatted_phone, otp)
    if not verified:
        return jsonify({'success': False, 'message': msg}), 400

    # Locate or create user
    user = User.query.filter_by(phone=formatted_phone).first()

    if not user:
        # Check if email provided already matches an account
        if email:
            user = User.query.filter_by(email=email).first()

        if user:
            user.phone = formatted_phone
            user.phone_verified = True
            if name and not user.name:
                user.name = name
        else:
            cust_name = name if name else f"Customer {clean_digits[-4:]}"
            user_email = email if email else f"{clean_digits}@phone.avyro.com"
            from werkzeug.security import generate_password_hash
            user = User(
                name=cust_name,
                phone=formatted_phone,
                email=user_email,
                password_hash=generate_password_hash(os.urandom(24).hex()),
                phone_verified=True,
                is_admin=False
            )
            db.session.add(user)
        db.session.commit()
    else:
        user.phone_verified = True
        if name and not user.name:
            user.name = name
        if email and not user.email:
            user.email = email
        db.session.commit()

    login_user(user, remember=True)
    merge_guest_cart_to_user(user)

    redirect_target = next_url or url_for('orders.checkout') if session.get('checkout_draft') else url_for('account.account')
    return jsonify({
        'success': True,
        'message': f'Welcome back, {user.name}!',
        'redirect_url': redirect_target
    })


@auth_bp.route('/auth/google')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('account.account'))

    next_url = request.args.get('next', '')
    auth_url, err = get_google_auth_url(next_url=next_url)

    if err:
        flash(f'Google Sign-In Notice: {err} Please use Phone OTP authentication or configure GOOGLE_CLIENT_ID in server environment.', 'warning')
        return redirect(url_for('auth.customer_auth', next=next_url))

    return redirect(auth_url)


@auth_bp.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        flash('Google authentication request was cancelled or failed.', 'danger')
        return redirect(url_for('auth.customer_auth'))

    user_info, err = exchange_google_code_for_user(code)
    if err or not user_info:
        flash(f'Google login error: {err or "Could not retrieve Google profile"}', 'danger')
        return redirect(url_for('auth.customer_auth'))

    google_id = user_info.get('id') or user_info.get('sub')
    email = user_info.get('email', '').lower()
    name = user_info.get('name') or user_info.get('given_name') or 'Google Customer'

    if not google_id or not email:
        flash('Google account did not return a valid profile ID or email address.', 'danger')
        return redirect(url_for('auth.customer_auth'))

    # Locate existing user by google_id or email
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            if name and not user.name:
                user.name = name
        else:
            user = User(
                name=name,
                email=email,
                google_id=google_id,
                password_hash=generate_password_hash(os.urandom(24).hex()),
                is_admin=False
            )
            db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    merge_guest_cart_to_user(user)

    next_page = session.pop('oauth_next', None) or url_for('account.account')
    flash(f'Welcome, {user.name}! Signed in via Google.', 'success')
    return redirect(next_page)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('checkout_draft', None)
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('shop.home'))
