import uuid
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
from app.extensions import db
from app.models import Cart, CartItem, Product

cart_bp = Blueprint('cart', __name__)

def get_or_create_cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    else:
        session_id = session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['cart_session_id'] = session_id

        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        return cart


@cart_bp.route('/cart')
def view_cart():
    cart = get_or_create_cart()
    subtotal = cart.total_price
    shipping = 0.0 if subtotal > 1000 or subtotal == 0 else 99.0
    grand_total = subtotal + shipping

    return render_template('cart.html', cart=cart, subtotal=subtotal, shipping=shipping, grand_total=grand_total)


@cart_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product or not product.status:
        return jsonify({'success': False, 'message': 'Product not found or unavailable'}), 444

    if product.stock < quantity:
        return jsonify({'success': False, 'message': f'Only {product.stock} units available in stock'}), 400

    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

    if cart_item:
        if cart_item.quantity + quantity > product.stock:
            return jsonify({'success': False, 'message': f'Cannot add more. Max available stock is {product.stock}'}), 400
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Added "{product.name}" to your cart!',
        'cart_count': cart.total_items,
        'cart_total': cart.total_price
    })


@cart_bp.route('/api/cart/update', methods=['POST'])
def update_cart_item():
    data = request.get_json() or {}
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        subtotal = cart.total_price
        shipping = 0.0 if subtotal > 1000 or subtotal == 0 else 99.0
        return jsonify({
            'success': True,
            'message': 'Item removed',
            'removed': True,
            'cart_count': cart.total_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'grand_total': subtotal + shipping
        })

    if quantity > cart_item.product.stock:
        return jsonify({'success': False, 'message': f'Max available stock is {cart_item.product.stock}'}), 400

    cart_item.quantity = quantity
    db.session.commit()

    subtotal = cart.total_price
    shipping = 0.0 if subtotal > 1000 or subtotal == 0 else 99.0

    return jsonify({
        'success': True,
        'message': 'Cart updated',
        'item_subtotal': cart_item.subtotal,
        'cart_count': cart.total_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'grand_total': subtotal + shipping
    })


@cart_bp.route('/api/cart/remove', methods=['POST'])
def remove_cart_item():
    data = request.get_json() or {}
    item_id = data.get('item_id')

    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    subtotal = cart.total_price
    shipping = 0.0 if subtotal > 1000 or subtotal == 0 else 99.0

    return jsonify({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': cart.total_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'grand_total': subtotal + shipping
    })


@cart_bp.route('/api/cart/count')
def cart_count():
    cart = get_or_create_cart()
    return jsonify({'cart_count': cart.total_items, 'cart_total': cart.total_price})
