import sys
import os

# Add root directory to python search path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db

app = create_app()

# Initialize database schema safely without network calls
with app.app_context():
    try:
        db.create_all()
        from app.models import Category, User, Product
        if not Category.query.first():
            if not User.query.filter_by(email='admin@avyro.com').first():
                admin = User(name='AVYRO Administrator', email='admin@avyro.com', is_admin=True)
                admin.set_password('Admin@123')
                db.session.add(admin)
            
            cat1 = Category(name='Audio & Sound', slug='audio-sound', image='cat-audio.jpg', description='Studio quality headphones.')
            cat2 = Category(name='Smart Wearables', slug='smart-wearables', image='cat-wearables.jpg', description='Smartwatches & trackers.')
            cat3 = Category(name='Tech Accessories', slug='tech-accessories', image='cat-accessories.jpg', description='Power banks & cables.')
            cat4 = Category(name='Modern Living', slug='modern-living', image='cat-living.jpg', description='Desk lifestyle gear.')
            db.session.add_all([cat1, cat2, cat3, cat4])
            db.session.commit()

            p1 = Product(name='AVYRO Studio Wireless Headphones Pro', slug='avyro-studio-wireless-headphones-pro', sku='AVY-AUD-001', description='Over-ear active noise-cancelling wireless headphones.', short_description='Over-ear active noise-cancelling headphones.', price=8999.0, sale_price=6499.0, stock=20, category_id=cat1.id, brand='AVYRO', featured=True, bestseller=True)
            p2 = Product(name='AVYRO Pulse Smartwatch Ultra 2', slug='avyro-pulse-smartwatch-ultra-2', sku='AVY-WR-001', description='Titanium case smartwatch with AMOLED display.', short_description='Titanium case smartwatch.', price=11999.0, sale_price=8999.0, stock=14, category_id=cat2.id, brand='AVYRO', featured=True, bestseller=True)
            p3 = Product(name='AVYRO Magnetic Power Bank 10,000mAh', slug='avyro-magnetic-power-bank-10k', sku='AVY-ACC-001', description='Slim MagSafe wireless power bank.', short_description='MagSafe power bank.', price=3499.0, sale_price=2499.0, stock=35, category_id=cat3.id, brand='AVYRO', featured=True)
            p4 = Product(name='AVYRO Ergonomic Aluminum Laptop Stand', slug='avyro-ergonomic-aluminum-laptop-stand', sku='AVY-DESK-001', description='CNC aluminum riser stand.', short_description='CNC aluminum laptop stand.', price=2999.0, sale_price=1999.0, stock=18, category_id=cat4.id, brand='AVYRO', bestseller=True)
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()
    except Exception as e:
        print(f"Fast seed notice: {e}")

# Vercel WSGI entry point
app = app
