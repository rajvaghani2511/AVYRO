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
            
            c1 = Category(name='Kitchen & Dining', slug='kitchen-dining', image='cat-kitchen-dining.jpg', description='Essential kitchen tools, utensils, oil dispensers, and dining accessories.')
            c2 = Category(name='Home Organization & Storage', slug='home-organization-storage', image='cat-organization.jpg', description='Storage bags, wardrobe organizers, drawer boxes, and hooks.')
            c3 = Category(name='Cleaning & Household', slug='cleaning-household', image='cat-cleaning.jpg', description='Mops, cleaning brushes, scrubbers, and dusting accessories.')
            c4 = Category(name='Home Improvement & Utility', slug='home-improvement-utility', image='cat-improvement.jpg', description='Adhesive hooks, cable management, repair tools, and door utility.')
            c5 = Category(name='Bathroom Accessories', slug='bathroom-accessories', image='cat-bathroom.jpg', description='Soap dispensers, organizers, toothbrush holders, and shower accessories.')
            c6 = Category(name='Home Decor & Lifestyle', slug='home-decor-lifestyle', image='cat-decor.jpg', description='Table decor, wall accents, desk items, and small lifestyle accessories.')
            c7 = Category(name='Laundry & Household Care', slug='laundry-household-care', image='cat-laundry.jpg', description='Laundry bags, drying racks, cloth clips, and hangers.')
            c8 = Category(name='Kitchen Storage', slug='kitchen-storage', image='cat-storage.jpg', description='Airtight containers, spice jars, refrigerator racks, and storage baskets.')
            c9 = Category(name='Serveware & Dining', slug='serveware-dining', image='cat-serveware.jpg', description='Plates, bowls, ceramic mugs, cutlery, and serving trays.')
            c10 = Category(name='Home Essentials', slug='home-essentials', image='cat-essentials.jpg', description='Daily use household items, space-saving gadgets, and utility essentials.')
            
            db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
            db.session.commit()

            p1 = Product(name='AVYRO Stainless Steel Oil Dispenser & Sprayer (1000ml)', slug='avyro-stainless-steel-oil-dispenser-1l', sku='AVY-HK-001', description='Premium food-grade 304 stainless steel oil dispenser with anti-drip nozzle.', short_description='Leak-proof 1000ml stainless steel oil dispenser.', price=899.0, sale_price=549.0, stock=45, category_id=c1.id, brand='AVYRO Home', featured=True, bestseller=True)
            p2 = Product(name='AVYRO 360° Rotating Spice & Masala Rack (16 Jars)', slug='avyro-360-rotating-spice-rack-16-jars', sku='AVY-HK-002', description='Revolving 16-piece spice organizer tower with 3-option shaker lids.', short_description='Revolving spice organizer tower with 16 jars.', price=1499.0, sale_price=999.0, stock=30, category_id=c8.id, brand='AVYRO Home', featured=True, bestseller=True)
            p3 = Product(name='AVYRO Heavy-Duty Natural Bamboo Chopping Board', slug='avyro-bamboo-chopping-board', sku='AVY-HK-003', description='Eco-friendly organic bamboo cutting board with juice groove.', short_description='Antibacterial organic bamboo cutting board.', price=999.0, sale_price=649.0, stock=50, category_id=c1.id, brand='AVYRO Home', featured=True)
            p4 = Product(name='AVYRO Airtight Food Storage Containers (Set of 6)', slug='avyro-airtight-food-storage-containers-set-6', sku='AVY-HK-004', description='Modular stackable container set with 4-sided locking lids.', short_description='Stackable BPA-free airtight container set.', price=1799.0, sale_price=1199.0, stock=25, category_id=c8.id, brand='AVYRO Home', bestseller=True)
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()
    except Exception as e:
        print(f"Fast seed notice: {e}")

# Vercel WSGI entry point
app = app
