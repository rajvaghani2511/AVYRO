from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.models import Product, Category, Wishlist, db

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')
def home():
    featured_categories = Category.query.filter_by(status=True).limit(6).all()
    trending_products = Product.query.filter_by(status=True, featured=True).limit(8).all()
    best_sellers = Product.query.filter_by(status=True, bestseller=True).limit(8).all()
    new_arrivals = Product.query.filter_by(status=True).order_by(Product.created_at.desc()).limit(8).all()

    # User wishlist IDs if logged in
    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = set(w.product_id for w in Wishlist.query.filter_by(user_id=current_user.id).all())

    return render_template('home.html',
                           featured_categories=featured_categories,
                           trending_products=trending_products,
                           best_sellers=best_sellers,
                           new_arrivals=new_arrivals,
                           user_wishlist_ids=user_wishlist_ids)


@shop_bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock', type=int)

    query = Product.query.filter_by(status=True)

    # Search filter
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(search)) |
            (Product.sku.ilike(search)) |
            (Product.description.ilike(search)) |
            (Product.short_description.ilike(search))
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            sub_ids = [sub.id for sub in selected_category.subcategories]
            cat_ids = [selected_category.id] + sub_ids
            query = query.filter(Product.category_id.in_(cat_ids))

    # Price filters
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Stock filter
    if in_stock == 1:
        query = query.filter(Product.stock > 0)

    # Sorting
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'popular':
        query = query.order_by(Product.bestseller.desc(), Product.featured.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    products_list = pagination.items

    categories = Category.query.filter_by(status=True, parent_id=None).all()

    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = set(w.product_id for w in Wishlist.query.filter_by(user_id=current_user.id).all())

    return render_template('shop.html',
                           products=products_list,
                           pagination=pagination,
                           categories=categories,
                           selected_category=selected_category,
                           search_query=search_query,
                           sort_by=sort_by,
                           min_price=min_price,
                           max_price=max_price,
                           in_stock=in_stock,
                           user_wishlist_ids=user_wishlist_ids)


@shop_bp.route('/category/<slug>')
def category_view(slug):
    category = Category.query.filter_by(slug=slug, status=True).first_or_404()
    sub_ids = [sub.id for sub in category.subcategories]
    cat_ids = [category.id] + sub_ids

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'newest')

    query = Product.query.filter(Product.status == True, Product.category_id.in_(cat_ids))
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'popular':
        query = query.order_by(Product.bestseller.desc(), Product.featured.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(status=True).all()

    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = set(w.product_id for w in Wishlist.query.filter_by(user_id=current_user.id).all())

    return render_template('shop.html',
                           products=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           selected_category=category,
                           search_query='',
                           sort_by=sort_by,
                           user_wishlist_ids=user_wishlist_ids)


@shop_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, status=True).first_or_404()
    related_products = Product.query.filter(
        Product.status == True,
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    is_in_wishlist = False
    if current_user.is_authenticated:
        is_in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None

    return render_template('product.html',
                           product=product,
                           related_products=related_products,
                           is_in_wishlist=is_in_wishlist)


@shop_bp.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    search = f"%{q}%"
    products = Product.query.filter(
        Product.status == True,
        (Product.name.ilike(search)) | (Product.brand.ilike(search))
    ).limit(6).all()

    results = []
    for p in products:
        results.append({
            'name': p.name,
            'slug': p.slug,
            'price': p.effective_price,
            'image': p.main_image,
            'category': p.category.name if p.category else ''
        })
    return jsonify(results)
