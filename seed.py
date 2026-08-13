import os
import urllib.request
from app import create_app
from app.extensions import db
from app.models import User, Category, Product, ProductImage, Address, Order, OrderItem

app = create_app()

def download_or_create_placeholder(filename, url):
    uploads_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)

    if not os.path.exists(filepath):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Downloaded image asset: {filename}")
        except Exception as e:
            print(f"Fallback for {filename}: {e}")
            # Create simple fallback text image if offline
            with open(filepath, 'wb') as f:
                f.write(b"")

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database schema cleared & re-created.")

        # 1. Download Seed Images
        sample_images = {
            'cat-audio.jpg': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
            'cat-wearables.jpg': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80',
            'cat-accessories.jpg': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&auto=format&fit=crop&q=80',
            'cat-living.jpg': 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&auto=format&fit=crop&q=80',
            'prod-headphones-1.jpg': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
            'prod-headphones-2.jpg': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80',
            'prod-smartwatch-1.jpg': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80',
            'prod-powerbank-1.jpg': 'https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=800&auto=format&fit=crop&q=80',
            'prod-laptopstand-1.jpg': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=80',
            'prod-earbuds-1.jpg': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
            'prod-deskmat-1.jpg': 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&auto=format&fit=crop&q=80',
            'prod-smartring-1.jpg': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80',
            'prod-flask-1.jpg': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=80',
            'default-product.webp': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&auto=format&fit=crop&q=80',
            'default-category.webp': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&auto=format&fit=crop&q=80'
        }

        print("Downloading demo image assets...")
        for fname, img_url in sample_images.items():
            download_or_create_placeholder(fname, img_url)

        # 2. Seed Users
        admin = User(
            name="AVYRO Administrator",
            email="admin@avyro.com",
            phone="+91 98765 00000",
            is_admin=True
        )
        admin.set_password("Admin@123")

        customer = User(
            name="Vikramaditya Sharma",
            email="user@avyro.com",
            phone="+91 98765 43210",
            is_admin=False
        )
        customer.set_password("User@123")

        db.session.add(admin)
        db.session.add(customer)
        db.session.flush()

        # 3. Seed Address for Demo Customer
        cust_address = Address(
            user_id=customer.id,
            name=customer.name,
            phone=customer.phone,
            address="702, Skyline Towers, Sector 62",
            city="Noida",
            state="Uttar Pradesh",
            pincode="201301",
            country="India",
            is_default=True
        )
        db.session.add(cust_address)

        # 4. Seed Categories
        cat_audio = Category(name="Audio & Sound", slug="audio-sound", description="Studio quality wireless headphones & spatial audio earbuds.", image="cat-audio.jpg")
        cat_wearables = Category(name="Smart Wearables", slug="smart-wearables", description="Next-gen smartwatches & health tracking rings.", image="cat-wearables.jpg")
        cat_tech = Category(name="Tech Accessories", slug="tech-accessories", description="MagSafe power banks, cables & desk stands.", image="cat-accessories.jpg")
        cat_living = Category(name="Modern Living", slug="modern-living", description="Ergonomic desk accessories & everyday lifestyle gear.", image="cat-living.jpg")

        db.session.add_all([cat_audio, cat_wearables, cat_tech, cat_living])
        db.session.flush()

        # 5. Seed 8+ Realistic Products
        products_data = [
            {
                "name": "AVYRO Studio Wireless Headphones Pro",
                "slug": "avyro-studio-wireless-headphones-pro",
                "sku": "AVY-AUD-001",
                "price": 8999.00,
                "sale_price": 6499.00,
                "stock": 20,
                "category_id": cat_audio.id,
                "brand": "AVYRO",
                "weight": "260g",
                "dimensions": "19 x 17 x 8 cm",
                "short_description": "Over-ear active noise-cancelling wireless headphones with 40-hour playback and memory foam earcups.",
                "description": "Engineered for pure audiophile precision. Features custom 40mm titanium drivers, hybrid ANC with transparency mode, ultra-low latency Bluetooth 5.3, and multi-point device connectivity. Designed with brushed aerospace aluminum arms and plush protein leather cushions.",
                "featured": True,
                "bestseller": True,
                "images": ["prod-headphones-1.jpg", "prod-headphones-2.jpg"]
            },
            {
                "name": "AVYRO Pulse Smartwatch Ultra 2",
                "slug": "avyro-pulse-smartwatch-ultra-2",
                "sku": "AVY-WR-001",
                "price": 11999.00,
                "sale_price": 8999.00,
                "stock": 14,
                "category_id": cat_wearables.id,
                "brand": "AVYRO",
                "weight": "54g",
                "dimensions": "49 x 44 x 12 mm",
                "short_description": "Titanium case smartwatch with 1000-nit AMOLED display, ECG monitoring, and dual-frequency GPS.",
                "description": "Crafted from Grade 5 titanium with sapphire crystal glass. Features continuous SpO2, heart rate monitoring, body temperature sensor, and over 100 indoor/outdoor sports modes. 10-day battery life on a single fast charge.",
                "featured": True,
                "bestseller": True,
                "images": ["prod-smartwatch-1.jpg"]
            },
            {
                "name": "AVYRO Magnetic Power Bank 10,000mAh",
                "slug": "avyro-magnetic-power-bank-10k",
                "sku": "AVY-ACC-001",
                "price": 3499.00,
                "sale_price": 2499.00,
                "stock": 35,
                "category_id": cat_tech.id,
                "brand": "AVYRO",
                "weight": "195g",
                "dimensions": "10 x 6.5 x 1.8 cm",
                "short_description": "Slim MagSafe wireless power bank with 22.5W USB-C PD fast charging and foldable kickstand.",
                "description": "Ultra-strong N52 magnetic array snaps directly to your phone. Delivers up to 15W wireless fast charging and 22.5W wired USB-C Power Delivery. Built-in zinc alloy kickstand for hands-free viewing while charging.",
                "featured": True,
                "bestseller": False,
                "images": ["prod-powerbank-1.jpg"]
            },
            {
                "name": "AVYRO Ergonomic Aluminum Laptop Stand",
                "slug": "avyro-ergonomic-aluminum-laptop-stand",
                "sku": "AVY-DESK-001",
                "price": 2999.00,
                "sale_price": 1999.00,
                "stock": 18,
                "category_id": cat_living.id,
                "brand": "AVYRO",
                "weight": "850g",
                "dimensions": "26 x 23 x 15 cm",
                "short_description": "Adjustable height CNC aluminum riser stand for MacBooks and laptops up to 17 inches.",
                "description": "Transform your desk ergonomics. Precision carved from anodized aluminum alloy with non-slip silicone padding. Elevates your laptop screen to eye level to prevent neck fatigue while optimizing passive heat airflow.",
                "featured": False,
                "bestseller": True,
                "images": ["prod-laptopstand-1.jpg"]
            },
            {
                "name": "AVYRO Spatial TWS Earbuds Air",
                "slug": "avyro-spatial-tws-earbuds-air",
                "sku": "AVY-AUD-002",
                "price": 4999.00,
                "sale_price": 3499.00,
                "stock": 4,  # Low stock test
                "category_id": cat_audio.id,
                "brand": "AVYRO",
                "weight": "42g with case",
                "dimensions": "6 x 4.5 x 2.2 cm",
                "short_description": "Low-latency wireless earbuds with spatial audio head tracking and IPX5 water resistance.",
                "description": "Immersive 3D audio experience with dynamic head tracking. Quad microphones with AI ENC clear voice reduction during calls. Wireless charging case provides 32 total hours of playback.",
                "featured": True,
                "bestseller": False,
                "images": ["prod-earbuds-1.jpg"]
            },
            {
                "name": "AVYRO Minimalist Vegan Leather Desk Mat",
                "slug": "avyro-minimalist-vegan-leather-desk-mat",
                "sku": "AVY-DESK-002",
                "price": 1899.00,
                "sale_price": 1299.00,
                "stock": 40,
                "category_id": cat_living.id,
                "brand": "AVYRO",
                "weight": "450g",
                "dimensions": "90 x 40 cm",
                "short_description": "Water-resistant premium dual-sided vegan leather mousepad and desk protector.",
                "description": "Elevate your workspace setup. Features a smooth polyurethane leather surface on one side and eco-felt on the reverse. Waterproof, easy to clean with a damp cloth, and spacious enough for keyboard, mouse, and coffee mug.",
                "featured": False,
                "bestseller": True,
                "images": ["prod-deskmat-1.jpg"]
            },
            {
                "name": "AVYRO Smart Health Ring Gen-3",
                "slug": "avyro-smart-health-ring-gen-3",
                "sku": "AVY-WR-002",
                "price": 14999.00,
                "sale_price": 11999.00,
                "stock": 10,
                "category_id": cat_wearables.id,
                "brand": "AVYRO",
                "weight": "4g",
                "dimensions": "Size 8-11 available",
                "short_description": "Sleek medical-grade titanium ring for 24/7 sleep tracking, HRV metrics, and readiness scores.",
                "description": "Discreet, screenless health tracking. Crafted from hypoallergenic titanium with diamond-like carbon coating. Tracks sleep stages, recovery, temperature variations, and daily activity. 7-day battery life with 100m water resistance.",
                "featured": True,
                "bestseller": False,
                "images": ["prod-smartring-1.jpg"]
            },
            {
                "name": "AVYRO Vacuum Insulated Steel Flask 750ml",
                "slug": "avyro-vacuum-insulated-steel-flask-750ml",
                "sku": "AVY-LIV-001",
                "price": 1699.00,
                "sale_price": 1199.00,
                "stock": 2,  # Low stock test
                "category_id": cat_living.id,
                "brand": "AVYRO",
                "weight": "380g",
                "dimensions": "28 x 7.5 cm",
                "short_description": "Double-wall 18/8 stainless steel bottle keeping drinks cold for 24h or hot for 12h.",
                "description": "BPA-free powder-coated finish with leakproof magnetic cap. Fits standard car cup holders. Perfect for workouts, office, and travel.",
                "featured": False,
                "bestseller": False,
                "images": ["prod-flask-1.jpg"]
            }
        ]

        for pdata in products_data:
            imgs = pdata.pop("images")
            product = Product(**pdata)
            db.session.add(product)
            db.session.flush()

            for i, img_path in enumerate(imgs):
                pi = ProductImage(product_id=product.id, image_path=img_path, sort_order=i)
                db.session.add(pi)

        # 6. Seed Sample Initial Order for Analytics
        headphone_prod = Product.query.filter_by(sku="AVY-AUD-001").first()
        order = Order(
            order_number="AVY-20260813-1001",
            user_id=customer.id,
            total_amount=6499.00,
            shipping_amount=0.0,
            discount_amount=0.0,
            payment_status="Paid",
            order_status="Delivered",
            shipping_name=customer.name,
            shipping_email=customer.email,
            shipping_phone=customer.phone,
            shipping_address=cust_address.address,
            shipping_city=cust_address.city,
            shipping_state=cust_address.state,
            shipping_pincode=cust_address.pincode,
            shipping_country="India"
        )
        db.session.add(order)
        db.session.flush()

        order_item = OrderItem(
            order_id=order.id,
            product_id=headphone_prod.id,
            product_name=headphone_prod.name,
            price=headphone_prod.effective_price,
            quantity=1
        )
        db.session.add(order_item)

        db.session.commit()
        print("==================================================")
        print("  AVYRO Seed Complete!")
        print("  Admin Login: admin@avyro.com / Admin@123")
        print("  Customer Login: user@avyro.com / User@123")
        print("  Categories Seeded: 4")
        print("  Products Seeded: 8")
        print("==================================================")

if __name__ == '__main__':
    seed_database()
