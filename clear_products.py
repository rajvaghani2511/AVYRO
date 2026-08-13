from app import create_app
from app.extensions import db
from app.models import Product, ProductImage, CartItem, OrderItem, Wishlist

app = create_app()

def clear_all_products():
    with app.app_context():
        print("Clearing all products and product images...")
        try:
            db.session.query(OrderItem).delete()
            db.session.query(CartItem).delete()
            db.session.query(Wishlist).delete()
            db.session.query(ProductImage).delete()
            db.session.query(Product).delete()
            db.session.commit()
            print("Successfully deleted all products! You can now add products one-by-one from the Admin Panel.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing products: {e}")

if __name__ == '__main__':
    clear_all_products()
