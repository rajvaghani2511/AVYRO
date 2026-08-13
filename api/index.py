import sys
import os

# Add root directory to python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, ProductImage

app = create_app()

def auto_seed_if_empty():
    with app.app_context():
        db.create_all()
        # Seed default admin if missing
        if not User.query.filter_by(email='admin@avyro.com').first():
            try:
                from seed import seed_database
                seed_database()
            except Exception as e:
                print(f"Auto-seed warning: {e}")

auto_seed_if_empty()

# Vercel WSGI Handler
handler = app
