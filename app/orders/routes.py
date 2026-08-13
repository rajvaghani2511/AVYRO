import urllib.request
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Cart, Order, OrderItem, Address, Product
from app.location_data import search_cities, search_states, lookup_local_pincode

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    date_str = datetime.datetime.utcnow().strftime('%Y%m%d')
    random_digits = str(random.randint(1000, 9999))
    return f"AVY-{date_str}-{random_digits}"

@orders_bp.route('/api/location/cities')
def api_search_cities():
    q = request.args.get('q', '')
    results = search_cities(q)
    return jsonify(results)

@orders_bp.route('/api/location/states')
def api_search_states():
    q = request.args.get('q', '')
    results = search_states(q)
    return jsonify(results)

@orders_bp.route('/api/pincode/lookup/<pincode>')
def api_pincode_lookup(pincode):
    pincode = (pincode or '').strip()
    if len(pincode) != 6 or not pincode.isdigit() or pincode[0] == '0' or pincode in {'000000', '123456', '111111', '999999'}:
        return jsonify({'valid': False, 'message': 'Invalid Indian PIN code. Must be 6 valid numeric digits.'}), 400

    # Try official India Post API first
    try:
        req = urllib.request.Request(
            f'https://api.postalpincode.in/pincode/{pincode}',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            if data and isinstance(data, list) and len(data) > 0:
                res = data[0]
                if res.get('Status') == 'Success' and res.get('PostOffice'):
                    post_offices = res['PostOffice']
                    districts = list(set([po['District'] for po in post_offices if po.get('District')]))
                    states = list(set([po['State'] for po in post_offices if po.get('State')]))
                    places = list(set([po['Name'] for po in post_offices if po.get('Name')]))

                    city = districts[0] if districts else (places[0] if places else '')
                    state = states[0] if states else ''

                    return jsonify({
                        'valid': True,
                        'city': city,
                        'state': state,
                        'districts': districts,
                        'states': states,
                        'places': places,
                        'pincode': pincode
                    })
                elif res.get('Status') == 'Error':
                    return jsonify({'valid': False, 'message': 'Invalid Indian postal PIN code.'}), 400
    except Exception as e:
        print(f"India Post API lookup notice ({pincode}):", e)

    # Fallback to local dataset lookup if API is unreachable
    local = lookup_local_pincode(pincode)
    if local and local.get('valid'):
        return jsonify(local)

    return jsonify({'valid': False, 'message': 'Invalid Indian PIN code.'}), 400


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
    shipping = 0.0
    discount = 0.0
    grand_total = subtotal - discount

    # Pre-fill address if logged in
    default_address = None
    if current_user.is_authenticated:
        default_address = Address.query.filter_by(user_id=current_user.id, is_default=True).first()
        if not default_address:
            default_address = Address.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        address_text = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        country = request.form.get('country', 'India').strip()
        payment_method = request.form.get('payment_method', 'cod')

        # Sanitize and validate 10-digit Indian phone number
        phone_digits = ''.join(filter(str.isdigit, phone_raw))
        if phone_digits.startswith('91') and len(phone_digits) == 12:
            phone_digits = phone_digits[2:]

        if len(phone_digits) != 10:
            flash('Please enter a valid 10-digit mobile number.', 'danger')
            return render_template('checkout.html', cart=cart, shipping=shipping, grand_total=grand_total, default_address=default_address)

        phone = f"+91 {phone_digits}"

        if not all([full_name, email, phone_digits, address_text, city, state, pincode]):
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
