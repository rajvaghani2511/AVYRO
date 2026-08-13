import os
from flask import Flask, render_template, session
from config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist safely
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.shop.routes import shop_bp
    from app.cart.routes import cart_bp
    from app.orders.routes import orders_bp
    from app.account.routes import account_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Global Context Processors for Templates
    @app.context_processor
    def inject_global_context():
        from flask_login import current_user
        from app.models import Category, Cart, CartItem, Wishlist

        categories = []
        cart_count = 0
        wishlist_count = 0

        try:
            categories = Category.query.filter_by(status=True, parent_id=None).all()
            if current_user.is_authenticated:
                user_cart = Cart.query.filter_by(user_id=current_user.id).first()
                if user_cart:
                    cart_count = user_cart.total_items
                wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            else:
                session_id = session.get('cart_session_id')
                if session_id:
                    guest_cart = Cart.query.filter_by(session_id=session_id).first()
                    if guest_cart:
                        cart_count = guest_cart.total_items
        except Exception as e:
            print(f"Global Context Processor Notice: {e}")

        return {
            'global_categories': categories,
            'global_cart_count': cart_count,
            'global_wishlist_count': wishlist_count
        }

    # Register custom jinja filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            if value is None or str(value).strip() == '':
                return "₹0"
            val = float(value)
            if val.is_integer():
                return f"₹{int(val):,}"
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0"

    @app.template_filter('img_url')
    def img_url_filter(filename):
        if not filename:
            return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'
        if filename.startswith('http://') or filename.startswith('https://'):
            return filename
        return f"/static/uploads/{filename}"

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
