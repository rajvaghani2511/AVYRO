import sys
import os

# Add root directory to python search path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, ProductImage

app = create_app()

# Initialize database schema safely without blocking network requests
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database init warning: {e}")

# Vercel WSGI entry point
app = app
