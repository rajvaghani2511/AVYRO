import sys
import os

# Add root directory to python search path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db

app = create_app()

_db_initialized = False

def sync_db_columns():
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        db_tables = inspector.get_table_names()
        for table_name, table in db.metadata.tables.items():
            if table_name in db_tables:
                existing_cols = {c['name'] for c in inspector.get_columns(table_name)}
                for col in table.columns:
                    if col.name not in existing_cols:
                        col_type = col.type.compile(db.engine.dialect)
                        nullable = "NULL" if col.nullable else "NOT NULL"
                        default = ""
                        if col.default is not None and col.default.arg is not None:
                            if isinstance(col.default.arg, bool):
                                default = f" DEFAULT {'TRUE' if col.default.arg else 'FALSE'}"
                            elif isinstance(col.default.arg, (int, float)):
                                default = f" DEFAULT {col.default.arg}"
                            elif isinstance(col.default.arg, str):
                                default = f" DEFAULT '{col.default.arg}'"
                        sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {col_type}{default} {nullable};'
                        db.session.execute(text(sql))
                        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Auto Column Sync Notice: {e}")

@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            db.create_all()
            sync_db_columns()
            from app.models import Category, User
            try:
                if not Category.query.first():
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
            except Exception as e:
                db.session.rollback()
                print(f"Category Seed Notice: {e}")

            try:
                if not User.query.filter_by(is_admin=True).first():
                    from werkzeug.security import generate_password_hash
                    admin = User(
                        name='AVYRO Administrator',
                        email='admin@avyro.com',
                        password_hash=generate_password_hash('Admin@123'),
                        is_admin=True
                    )
                    db.session.add(admin)
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Admin Seed Notice: {e}")

            _db_initialized = True
        except Exception as e:
            db.session.remove()
            print(f"Lazy DB Init Notice: {e}")

# Vercel WSGI entry point
app = app
