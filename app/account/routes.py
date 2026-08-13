from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Order, Address, Wishlist, Product

account_bp = Blueprint('account', __name__)

@account_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()

            if name:
                current_user.name = name
                current_user.phone = phone
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            else:
                flash('Name is required.', 'danger')

        elif action == 'add_address':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            address_text = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            country = request.form.get('country', 'India').strip()
            is_default = True if request.form.get('is_default') else False

            if all([name, phone, address_text, city, state, pincode]):
                if is_default:
                    Address.query.filter_by(user_id=current_user.id).update({'is_default': False})

                new_addr = Address(
                    user_id=current_user.id,
                    name=name,
                    phone=phone,
                    address=address_text,
                    city=city,
                    state=state,
                    pincode=pincode,
                    country=country,
                    is_default=is_default
                )
                db.session.add(new_addr)
                db.session.commit()
                flash('Address added successfully!', 'success')
            else:
                flash('Please complete all address fields.', 'danger')

        return redirect(url_for('account.account'))

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()

    return render_template('account.html',
                           orders=orders,
                           addresses=addresses,
                           wishlist_count=wishlist_count)


@account_bp.route('/address/delete/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    addr = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash('Address removed.', 'info')
    return redirect(url_for('account.account'))


@account_bp.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = [w.product for w in wishlist_items if w.product and w.product.status]
    return render_template('wishlist.html', products=products)


@account_bp.route('/api/wishlist/toggle', methods=['POST'])
def toggle_wishlist():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please login to save items to your wishlist', 'redirect': url_for('auth.login')}), 401

    data = request.get_json() or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID missing'}), 400

    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        added = False
        message = 'Removed from Wishlist'
    else:
        new_w = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(new_w)
        db.session.commit()
        added = True
        message = 'Added to Wishlist'

    wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()

    return jsonify({
        'success': True,
        'added': added,
        'message': message,
        'wishlist_count': wishlist_count
    })
