import os
import uuid
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, Product, ProductImage, Category, Order, OrderItem

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def save_upload_image(file):
    if not file or file.filename == '':
        return None
    
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return None

    # Check Cloudinary configuration
    if os.environ.get('CLOUDINARY_URL'):
        try:
            import cloudinary
            import cloudinary.uploader
            result = cloudinary.uploader.upload(file, folder="avyro_uploads")
            if result and 'secure_url' in result:
                return result['secure_url']
        except Exception as e:
            print(f"Cloudinary upload fallback to local storage: {e}")

    filename = f"{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid administrator credentials.', 'danger')
            return render_template('admin/login.html')

        if not user.is_admin:
            flash('Your account does not have administrator access permissions.', 'danger')
            return render_template('admin/login.html')

        login_user(user)
        flash(f'Admin portal authenticated. Welcome, {user.name}!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    total_orders = Order.query.count()

    # Revenue calculation
    orders = Order.query.all()
    total_revenue = sum(o.total_amount for o in orders if o.payment_status in ['Paid', 'Completed'] or o.order_status == 'Delivered')
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    low_stock_products = Product.query.filter(Product.stock <= 5).count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()
    low_stock_list = Product.query.filter(Product.stock <= 5).limit(6).all()

    # Analytics Data for Chart.js
    # 1. Revenue & Order Trends over the last 6 months
    today = datetime.utcnow()
    chart_months = []
    chart_revenue = []
    chart_orders = []

    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month_str = month_date.strftime('%b %Y')
        chart_months.append(month_str)
        
        # Calculate monthly totals
        month_start = datetime(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = datetime(month_date.year + 1, 1, 1)
        else:
            month_end = datetime(month_date.year, month_date.month + 1, 1)

        m_orders = Order.query.filter(Order.created_at >= month_start, Order.created_at < month_end).all()
        m_rev = sum(o.total_amount for o in m_orders if o.order_status != 'Cancelled')
        
        chart_revenue.append(round(m_rev, 2))
        chart_orders.append(len(m_orders))

    # 2. Category Product Distribution
    categories = Category.query.all()
    cat_names = [c.name for c in categories]
    cat_counts = [len(c.products) for c in categories]

    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_customers=total_customers,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           pending_orders=pending_orders,
                           low_stock_products=low_stock_products,
                           recent_orders=recent_orders,
                           low_stock_list=low_stock_list,
                           chart_months=chart_months,
                           chart_revenue=chart_revenue,
                           chart_orders=chart_orders,
                           cat_names=cat_names,
                           cat_counts=cat_counts)


@admin_bp.route('/products')
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Product.query

    if search:
        s = f"%{search}%"
        query = query.filter((Product.name.ilike(s)) | (Product.sku.ilike(s)))

    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    categories = Category.query.all()

    return render_template('admin/products.html',
                           products=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           search=search,
                           category_id=category_id)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    categories = Category.query.filter_by(status=True).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        sku = request.form.get('sku', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        sale_price = request.form.get('sale_price', type=float)
        stock = request.form.get('stock', type=int, default=0)
        description = request.form.get('description', '').strip()
        short_description = request.form.get('short_description', '').strip()
        brand = request.form.get('brand', 'AVYRO').strip()
        weight = request.form.get('weight', '').strip()
        dimensions = request.form.get('dimensions', '').strip()
        featured = True if request.form.get('featured') else False
        bestseller = True if request.form.get('bestseller') else False
        status = True if request.form.get('status') else False

        if not name or not sku or not category_id or price is None or not description:
            flash('Please fill in all required product fields.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        existing_sku = Product.query.filter_by(sku=sku).first()
        if existing_sku:
            flash(f'A product with SKU "{sku}" already exists.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        # Generate unique slug
        base_slug = Product.generate_slug(name)
        slug = base_slug
        counter = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product(
            name=name,
            slug=slug,
            sku=sku,
            category_id=category_id,
            price=price,
            sale_price=sale_price if sale_price and sale_price > 0 else None,
            stock=stock,
            description=description,
            short_description=short_description,
            brand=brand,
            weight=weight,
            dimensions=dimensions,
            featured=featured,
            bestseller=bestseller,
            status=status
        )
        db.session.add(product)
        db.session.flush()

        # Handle multiple uploaded images
        images = request.files.getlist('images')
        sort_order = 0
        for file in images:
            filename = save_upload_image(file)
            if filename:
                prod_img = ProductImage(product_id=product.id, image_path=filename, sort_order=sort_order)
                db.session.add(prod_img)
                sort_order += 1

        db.session.commit()
        flash(f'Product "{product.name}" created successfully!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.filter_by(status=True).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        sku = request.form.get('sku', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        sale_price = request.form.get('sale_price', type=float)
        stock = request.form.get('stock', type=int, default=0)
        description = request.form.get('description', '').strip()
        short_description = request.form.get('short_description', '').strip()
        brand = request.form.get('brand', 'AVYRO').strip()
        weight = request.form.get('weight', '').strip()
        dimensions = request.form.get('dimensions', '').strip()
        featured = True if request.form.get('featured') else False
        bestseller = True if request.form.get('bestseller') else False
        status = True if request.form.get('status') else False

        if not name or not sku or not category_id or price is None or not description:
            flash('Please fill in all required product fields.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        # SKU uniqueness check
        existing_sku = Product.query.filter(Product.sku == sku, Product.id != id).first()
        if existing_sku:
            flash(f'SKU "{sku}" is already in use by another product.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        if product.name != name:
            base_slug = Product.generate_slug(name)
            slug = base_slug
            counter = 1
            while Product.query.filter(Product.slug == slug, Product.id != id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug

        product.name = name
        product.sku = sku
        product.category_id = category_id
        product.price = price
        product.sale_price = sale_price if sale_price and sale_price > 0 else None
        product.stock = stock
        product.description = description
        product.short_description = short_description
        product.brand = brand
        product.weight = weight
        product.dimensions = dimensions
        product.featured = featured
        product.bestseller = bestseller
        product.status = status

        # Handle new image uploads
        images = request.files.getlist('images')
        sort_order = len(product.images)
        for file in images:
            filename = save_upload_image(file)
            if filename:
                prod_img = ProductImage(product_id=product.id, image_path=filename, sort_order=sort_order)
                db.session.add(prod_img)
                sort_order += 1

        db.session.commit()
        flash(f'Product "{product.name}" updated successfully.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" has been deleted.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/delete-image/<int:image_id>', methods=['POST'])
@admin_required
def delete_product_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    db.session.delete(image)
    db.session.commit()
    flash('Image removed.', 'info')
    return redirect(url_for('admin.edit_product', id=product_id))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            if name:
                existing = Category.query.filter_by(name=name).first()
                if existing:
                    flash(f'Category "{name}" already exists.', 'danger')
                else:
                    slug = Category.generate_slug(name)
                    file = request.files.get('image')
                    image_filename = save_upload_image(file) or 'default-category.webp'

                    cat = Category(name=name, slug=slug, description=description, image=image_filename)
                    db.session.add(cat)
                    db.session.commit()
                    flash(f'Category "{name}" added successfully.', 'success')

        elif action == 'edit':
            cat_id = request.form.get('category_id', type=int)
            cat = Category.query.get_or_404(cat_id)
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            if name:
                cat.name = name
                cat.slug = Category.generate_slug(name)
                cat.description = description
                file = request.files.get('image')
                if file and file.filename != '':
                    filename = save_upload_image(file)
                    if filename:
                        cat.image = filename
                db.session.commit()
                flash(f'Category "{name}" updated.', 'success')

        return redirect(url_for('admin.categories'))

    categories_list = Category.query.all()
    return render_template('admin/categories.html', categories=categories_list)


@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    if cat.products:
        flash(f'Cannot delete category "{cat.name}" because it contains products.', 'danger')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash(f'Category "{cat.name}" deleted.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status', '').strip()
    query = Order.query

    if status_filter:
        query = query.filter_by(order_status=status_filter)

    orders_list = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders_list, status_filter=status_filter)


@admin_bp.route('/orders/<int:id>', methods=['GET', 'POST'])
@admin_required
def order_detail(id):
    order = Order.query.get_or_404(id)

    if request.method == 'POST':
        new_order_status = request.form.get('order_status')
        new_payment_status = request.form.get('payment_status')

        if new_order_status:
            order.order_status = new_order_status
        if new_payment_status:
            order.payment_status = new_payment_status

        db.session.commit()
        flash(f'Order #{order.order_number} status updated to "{order.order_status}".', 'success')
        return redirect(url_for('admin.order_detail', id=order.id))

    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/customers')
@admin_required
def customers():
    customers_list = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()

    # Build customer stats dictionary
    customer_stats = {}
    for c in customers_list:
        user_orders = Order.query.filter_by(user_id=c.id).all()
        order_count = len(user_orders)
        total_spent = sum(o.total_amount for o in user_orders if o.order_status != 'Cancelled')
        customer_stats[c.id] = {
            'order_count': order_count,
            'total_spent': total_spent
        }

    return render_template('admin/customers.html', customers=customers_list, stats=customer_stats)
