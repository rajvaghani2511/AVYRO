from datetime import datetime
import re
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    cart = db.relationship('Cart', backref='user', uselist=False, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, default=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)

    @staticmethod
    def generate_slug(name):
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        return re.sub(r'[\s-]+', '-', slug).strip('-')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    sku = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand = db.Column(db.String(100), nullable=True, default='AVYRO')
    weight = db.Column(db.String(50), nullable=True)
    dimensions = db.Column(db.String(100), nullable=True)
    featured = db.Column(db.Boolean, default=False)
    bestseller = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan', order_by='ProductImage.sort_order')
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    wishlists = db.relationship('Wishlist', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan', order_by='Review.created_at.desc()')

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def effective_price(self):
        if self.sale_price and self.sale_price > 0 and self.sale_price < self.price:
            return round(self.sale_price, 2)
        return round(self.price, 2)

    @property
    def discount_percentage(self):
        if self.sale_price and self.sale_price > 0 and self.sale_price < self.price:
            return int(round((1 - (self.sale_price / self.price)) * 100))
        return 0

    @property
    def main_image(self):
        if self.images:
            return self.images[0].image_path
        return 'default-product.webp'

    @property
    def is_in_stock(self):
        return self.stock > 0

    @staticmethod
    def generate_slug(name):
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        return re.sub(r'[\s-]+', '-', slug).strip('-')

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    @property
    def subtotal(self):
        return round(self.product.effective_price * self.quantity, 2)


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='Pending')  # Pending, Paid, Failed
    order_status = db.Column(db.String(20), default='Pending')    # Pending, Confirmed, Processing, Shipped, Delivered, Cancelled

    # Shipping Details
    shipping_name = db.Column(db.String(100), nullable=False)
    shipping_email = db.Column(db.String(120), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_pincode = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(100), default='India')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @property
    def subtotal(self):
        return round(self.price * self.quantity, 2)


class Wishlist(db.Model):
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='India')
    is_default = db.Column(db.Boolean, default=False)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    title = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} for Product {self.product_id} by {self.reviewer_name}>'

