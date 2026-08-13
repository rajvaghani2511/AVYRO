import random
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Cart, Order, OrderItem, Address, Product

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    date_str = datetime.datetime.utcnow().strftime('%Y%m%d')
    random_digits = str(random.randint(1000, 9999))
    return f"AVY-{date_str}-{random_digits}"

@orders_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
    else:
        session_id = session.get('cart_session_id')
        cart = Cart.query.filter_by(session_id=session_id).first() if session_id else None

    if not cart or not cart.items:
        flash('Your shopping cart is empty.', 'warning')
        return redirect(url_for('shop.products'))

    # Check stock availability
    for item in cart.items:
        if item.quantity > item.product.stock:
            flash(f'Sorry, "{item.product.name}" has only {item.product.stock} units in stock.', 'danger')
            return redirect(url_for('cart.view_cart'))

    subtotal = cart.total_price
    shipping = 0.0 if subtotal > 1000 else 99.0
    discount = 0.0
    grand_total = subtotal + shipping - discount

    # Pre-fill address if logged in
    default_address = None
    if current_user.is_authenticated:
        default_address = Address.query.filter_by(user_id=current_user.id, is_default=True).first()
        if not default_address:
            default_address = Address.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address_text = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        country = request.form.get('country', 'India').strip()
        payment_method = request.form.get('payment_method', 'cod')

        if not all([full_name, email, phone, address_text, city, state, pincode]):
            flash('Please fill in all shipping details.', 'danger')
            return render_template('checkout.html', cart=cart, shipping=shipping, grand_total=grand_total, default_address=default_address)

        # Create user if guest checkout or save address if user requested
        user_id = current_user.id if current_user.is_authenticated else None
        
        # If logged in and save_address checked
        if current_user.is_authenticated and request.form.get('save_address'):
            new_addr = Address(
                user_id=current_user.id,
                name=full_name,
                phone=phone,
                address=address_text,
                city=city,
                state=state,
                pincode=pincode,
                country=country,
                is_default=True
            )
            db.session.add(new_addr)

        # Create Order
        order = Order(
            order_number=generate_order_number(),
            user_id=user_id,
            total_amount=grand_total,
            shipping_amount=shipping,
            discount_amount=discount,
            payment_status='Paid' if payment_method == 'card' else 'Pending (COD)',
            order_status='Pending',
            shipping_name=full_name,
            shipping_email=email,
            shipping_phone=phone,
            shipping_address=address_text,
            shipping_city=city,
            shipping_state=state,
            shipping_pincode=pincode,
            shipping_country=country
        )
        db.session.add(order)
        db.session.flush()

        # Create Order Items and update product stock
        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                product_name=item.product.name,
                price=item.product.effective_price,
                quantity=item.quantity
            )
            db.session.add(order_item)
            
            # Deduct stock
            item.product.stock -= item.quantity

        # Delete cart items
        for item in cart.items:
            db.session.delete(item)

        db.session.commit()

        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('orders.order_confirmation', order_number=order.order_number))

    return render_template('checkout.html',
                           cart=cart,
                           shipping=shipping,
                           grand_total=grand_total,
                           default_address=default_address)


@orders_bp.route('/order-confirmation/<order_number>')
def order_confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_confirmation.html', order=order)


@orders_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('order_detail_customer.html', order=order)
