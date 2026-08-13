import os
import sys
import urllib.request

# Ensure app context can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Category, Product, ProductImage, Address, Order, OrderItem, Cart, CartItem, Wishlist

app = create_app()

def download_or_create_placeholder(url, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        return
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Notice: Image download skipped for {filepath}: {e}")

def seed_database():
    with app.app_context():
        print("Safely re-creating database schema with parent_id support...")
        db.drop_all()
        db.create_all()

        # Download Home & Kitchen Category and Product Images
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        
        sample_images = {
            'cat-kitchen-dining.jpg': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80',
            'cat-organization.jpg': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=80',
            'cat-cleaning.jpg': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&auto=format&fit=crop&q=80',
            'cat-improvement.jpg': 'https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop&q=80',
            'cat-bathroom.jpg': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=80',
            'cat-decor.jpg': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=600&auto=format&fit=crop&q=80',
            'cat-laundry.jpg': 'https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?w=600&auto=format&fit=crop&q=80',
            'cat-storage.jpg': 'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=600&auto=format&fit=crop&q=80',
            'cat-serveware.jpg': 'https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=600&auto=format&fit=crop&q=80',
            'cat-essentials.jpg': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=80',
            
            # Product images
            'prod-oildispenser-1.jpg': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&auto=format&fit=crop&q=80',
            'prod-spicerack-1.jpg': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=800&auto=format&fit=crop&q=80',
            'prod-choppingboard-1.jpg': 'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=800&auto=format&fit=crop&q=80',
            'prod-containers-1.jpg': 'https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=800&auto=format&fit=crop&q=80',
            'prod-laundrybag-1.jpg': 'https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?w=800&auto=format&fit=crop&q=80',
            'prod-mopbucket-1.jpg': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&auto=format&fit=crop&q=80',
            'prod-flask-1.jpg': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=80',
            'prod-hooks-1.jpg': 'https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=800&auto=format&fit=crop&q=80',
            'prod-cups-1.jpg': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop&q=80',
            'prod-fridgeracks-1.jpg': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop&q=80',
        }

        for img_name, img_url in sample_images.items():
            download_or_create_placeholder(img_url, os.path.join(uploads_dir, img_name))

        # Clear existing categories and products safely
        print("Clearing old categories and products...")
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(CartItem).delete()
        db.session.query(Cart).delete()
        db.session.query(Wishlist).delete()
        db.session.query(ProductImage).delete()
        db.session.query(Product).delete()
        db.session.query(Category).delete()
        db.session.commit()

        # Seed 10 Home & Kitchen Main Categories & Subcategories
        hk_structure = [
            {
                "name": "Kitchen & Dining",
                "slug": "kitchen-dining",
                "image": "cat-kitchen-dining.jpg",
                "description": "Essential kitchen tools, utensils, oil dispensers, and dining accessories.",
                "subs": [
                    "Kitchen Tools & Accessories", "Cooking Utensils", "Kitchen Organizers", 
                    "Food Storage Containers", "Lunch Boxes", "Water Bottles", "Flasks & Thermos", 
                    "Kitchen Gadgets", "Measuring Tools", "Strainers & Colanders", 
                    "Chopping & Cutting Tools", "Baking Accessories", "Oil Dispensers & Sprayers", 
                    "Spice & Masala Storage", "Serving Accessories", "Dining Accessories"
                ]
            },
            {
                "name": "Home Organization & Storage",
                "slug": "home-organization-storage",
                "image": "cat-organization.jpg",
                "description": "Storage bags, wardrobe organizers, drawer boxes, and hooks.",
                "subs": [
                    "Storage Bags", "Storage Boxes", "Drawer Organizers", "Wardrobe Organizers", 
                    "Multipurpose Organizers", "Document & File Organizers", "Travel Storage", 
                    "Hooks & Hangers", "Shoe Storage", "Laundry Storage", "Cosmetic & Makeup Organizers"
                ]
            },
            {
                "name": "Cleaning & Household",
                "slug": "cleaning-household",
                "image": "cat-cleaning.jpg",
                "description": "Mops, cleaning brushes, scrubbers, and dusting accessories.",
                "subs": [
                    "Cleaning Brushes", "Floor Cleaning Tools", "Bathroom Cleaning", 
                    "Toilet Cleaning", "Kitchen Cleaning", "Dishwashing Accessories", 
                    "Shoe Cleaning", "Dusting Tools", "Scrubbers & Sponges", 
                    "Cleaning Accessories", "Household Cleaning Tools"
                ]
            },
            {
                "name": "Home Improvement & Utility",
                "slug": "home-improvement-utility",
                "image": "cat-improvement.jpg",
                "description": "Adhesive hooks, cable management, repair tools, and door utility.",
                "subs": [
                    "Adhesive Hooks", "Door Accessories", "Furniture Accessories", 
                    "Utility Tools", "Home Repair Accessories", "Sealing & Protection Products", 
                    "Cable Management", "Electrical Accessories", "Multipurpose Utility Products"
                ]
            },
            {
                "name": "Bathroom Accessories",
                "slug": "bathroom-accessories",
                "image": "cat-bathroom.jpg",
                "description": "Soap dispensers, organizers, toothbrush holders, and shower accessories.",
                "subs": [
                    "Bathroom Organizers", "Soap Holders", "Toothbrush Holders", 
                    "Bathroom Brushes", "Toilet Accessories", "Shower Accessories", 
                    "Bathroom Storage", "Drain & Cleaning Accessories"
                ]
            },
            {
                "name": "Home Decor & Lifestyle",
                "slug": "home-decor-lifestyle",
                "image": "cat-decor.jpg",
                "description": "Table decor, wall accents, desk items, and small lifestyle accessories.",
                "subs": [
                    "Decorative Accessories", "Table Decor", "Desk Accessories", 
                    "Home Utility Decor", "Wall Accessories", "Small Decorative Items", "Lifestyle Accessories"
                ]
            },
            {
                "name": "Laundry & Household Care",
                "slug": "laundry-household-care",
                "image": "cat-laundry.jpg",
                "description": "Laundry bags, drying racks, cloth clips, and hangers.",
                "subs": [
                    "Laundry Bags", "Clothes Organizers", "Hangers", "Cloth Clips", 
                    "Drying Accessories", "Laundry Accessories", "Household Care Products"
                ]
            },
            {
                "name": "Kitchen Storage",
                "slug": "kitchen-storage",
                "image": "cat-storage.jpg",
                "description": "Airtight containers, spice jars, refrigerator racks, and storage baskets.",
                "subs": [
                    "Food Storage Bags", "Containers", "Jars", "Spice Organizers", 
                    "Refrigerator Organizers", "Grain Storage", "Kitchen Racks", "Storage Baskets"
                ]
            },
            {
                "name": "Serveware & Dining",
                "slug": "serveware-dining",
                "image": "cat-serveware.jpg",
                "description": "Plates, bowls, ceramic mugs, cutlery, and serving trays.",
                "subs": [
                    "Plates", "Bowls", "Cups & Mugs", "Spoons & Cutlery", 
                    "Serving Trays", "Serving Bowls", "Dining Accessories", "Table Accessories"
                ]
            },
            {
                "name": "Home Essentials",
                "slug": "home-essentials",
                "image": "cat-essentials.jpg",
                "description": "Daily use household items, space-saving gadgets, and utility essentials.",
                "subs": [
                    "Household Essentials", "Multipurpose Products", "Daily Use Products", 
                    "Space Saving Products", "Utility Accessories", "Travel & Home Essentials"
                ]
            }
        ]

        created_sub_map = {}

        for main in hk_structure:
            parent_cat = Category(
                name=main["name"],
                slug=main["slug"],
                image=main["image"],
                description=main["description"],
                status=True
            )
            db.session.add(parent_cat)
            db.session.flush()

            for sub_name in main["subs"]:
                sub_slug = Category.generate_slug(sub_name)
                # Check if subcategory slug already created
                if Category.query.filter_by(slug=sub_slug).first():
                    sub_slug = f"{sub_slug}-{parent_cat.id}"
                
                sub_cat = Category(
                    name=sub_name,
                    slug=sub_slug,
                    description=f"{sub_name} for everyday Indian home and kitchen care.",
                    parent_id=parent_cat.id,
                    status=True
                )
                db.session.add(sub_cat)
                db.session.flush()
                created_sub_map[sub_name] = sub_cat.id

        db.session.commit()
        print("Home & Kitchen category structure created successfully!")

        # Helper to pick category ID
        def get_cat(name):
            cat = Category.query.filter_by(name=name).first()
            return cat.id if cat else 1

        # Seed Home & Kitchen Products
        products_data = [
            {
                "name": "AVYRO Stainless Steel Oil Dispenser & Sprayer (1000ml)",
                "slug": "avyro-stainless-steel-oil-dispenser-1l",
                "sku": "AVY-HK-001",
                "description": "Premium food-grade 304 stainless steel oil dispenser with anti-drip nozzle and transparent measurement window. Ideal for mustard oil, olive oil, ghee, and vinegar.",
                "short_description": "Leak-proof 1000ml stainless steel oil dispenser with anti-drip spout.",
                "price": 899.0,
                "sale_price": 549.0,
                "stock": 45,
                "category_id": get_cat("Oil Dispensers & Sprayers"),
                "brand": "AVYRO Home",
                "weight": "320g",
                "dimensions": "24 x 8 x 8 cm",
                "featured": True,
                "bestseller": True,
                "images": ["prod-oildispenser-1.jpg"]
            },
            {
                "name": "AVYRO 360° Rotating Spice & Masala Rack (16 Jars)",
                "slug": "avyro-360-rotating-spice-rack-16-jars",
                "sku": "AVY-HK-002",
                "description": "Revolving 16-piece spice organizer tower crafted from unbreakable BPA-free ABS plastic with chrome lids. Includes 3-option shaker lids for coarse and fine Indian masalas.",
                "short_description": "Revolving spice organizer tower with 16 airtight glass jars.",
                "price": 1499.0,
                "sale_price": 999.0,
                "stock": 30,
                "category_id": get_cat("Spice & Masala Storage"),
                "brand": "AVYRO Home",
                "weight": "1.2kg",
                "dimensions": "28 x 18 x 18 cm",
                "featured": True,
                "bestseller": True,
                "images": ["prod-spicerack-1.jpg"]
            },
            {
                "name": "AVYRO Heavy-Duty Natural Bamboo Chopping Board",
                "slug": "avyro-bamboo-chopping-board",
                "sku": "AVY-HK-003",
                "description": "Eco-friendly organic bamboo cutting board with built-in juice groove and handle slot. Naturally antibacterial, knife-friendly, and warp resistant.",
                "short_description": "Antibacterial organic bamboo cutting board with juice groove.",
                "price": 999.0,
                "sale_price": 649.0,
                "stock": 50,
                "category_id": get_cat("Chopping & Cutting Tools"),
                "brand": "AVYRO Home",
                "weight": "750g",
                "dimensions": "34 x 24 x 1.8 cm",
                "featured": True,
                "bestseller": False,
                "images": ["prod-choppingboard-1.jpg"]
            },
            {
                "name": "AVYRO Airtight Food Storage Containers (Set of 6)",
                "slug": "avyro-airtight-food-storage-containers-set-6",
                "sku": "AVY-HK-004",
                "description": "Modular stackable container set with 4-sided locking lids and silicone seals. Perfect for pulses, rice, snacks, flour, and sugar.",
                "short_description": "Stackable BPA-free airtight container set for dry kitchen groceries.",
                "price": 1799.0,
                "sale_price": 1199.0,
                "stock": 25,
                "category_id": get_cat("Food Storage Containers"),
                "brand": "AVYRO Home",
                "weight": "1.1kg",
                "dimensions": "Various sizes (500ml - 2L)",
                "featured": True,
                "bestseller": True,
                "images": ["prod-containers-1.jpg"]
            },
            {
                "name": "AVYRO Collapsible Waterproof Laundry Storage Basket",
                "slug": "avyro-collapsible-laundry-storage-basket",
                "sku": "AVY-HK-005",
                "description": "Multi-purpose 60L linen cotton fabric laundry hamper with waterproof PE lining and sturdy leather handles. Folds flat when not in use.",
                "short_description": "Waterproof 60L linen fabric laundry hamper with leather handles.",
                "price": 799.0,
                "sale_price": 499.0,
                "stock": 40,
                "category_id": get_cat("Laundry Storage"),
                "brand": "AVYRO Home",
                "weight": "380g",
                "dimensions": "50 x 40 x 30 cm",
                "featured": False,
                "bestseller": True,
                "images": ["prod-laundrybag-1.jpg"]
            },
            {
                "name": "AVYRO Microfiber Flat Floor Cleaning Mop with Wringer Bucket",
                "slug": "avyro-microfiber-flat-floor-mop-bucket",
                "sku": "AVY-HK-006",
                "description": "Hands-free squeeze flat mop with twin chamber bucket for washing and drying. 360-degree rotating head reaches under furniture and tight corners.",
                "short_description": "Self-wringing flat mop with dual-chamber bucket and microfiber pads.",
                "price": 1999.0,
                "sale_price": 1299.0,
                "stock": 20,
                "category_id": get_cat("Floor Cleaning Tools"),
                "brand": "AVYRO Home",
                "weight": "1.6kg",
                "dimensions": "38 x 22 x 20 cm",
                "featured": True,
                "bestseller": True,
                "images": ["prod-mopbucket-1.jpg"]
            },
            {
                "name": "AVYRO Double-Wall Vacuum Insulated Flask Bottle (1000ml)",
                "slug": "avyro-vacuum-insulated-flask-bottle-1000ml",
                "sku": "AVY-HK-007",
                "description": "18/8 stainless steel thermo flask keeps beverages hot for 18 hours or cold for 24 hours. Sweat-free powder-coated exterior with leak-proof cap.",
                "short_description": "Heavy-duty 1L vacuum insulated hot & cold stainless steel bottle.",
                "price": 1299.0,
                "sale_price": 849.0,
                "stock": 35,
                "category_id": get_cat("Flasks & Thermos"),
                "brand": "AVYRO Home",
                "weight": "450g",
                "dimensions": "30 x 8.5 x 8.5 cm",
                "featured": False,
                "bestseller": True,
                "images": ["prod-flask-1.jpg"]
            },
            {
                "name": "AVYRO Heavy-Duty Adhesive Wall Utility Hooks (Pack of 10)",
                "slug": "avyro-heavy-duty-adhesive-utility-hooks-10",
                "sku": "AVY-HK-008",
                "description": "Transparent self-adhesive wall hooks holding up to 5kg per hook. Waterproof and oil-proof, ideal for kitchen utensils, towels, and keys without drilling.",
                "short_description": "No-drill waterproof self-adhesive wall hooks holding up to 5kg.",
                "price": 499.0,
                "sale_price": 299.0,
                "stock": 60,
                "category_id": get_cat("Adhesive Hooks"),
                "brand": "AVYRO Home",
                "weight": "120g",
                "dimensions": "6 x 6 cm per hook",
                "featured": False,
                "bestseller": False,
                "images": ["prod-hooks-1.jpg"]
            },
            {
                "name": "AVYRO Artisanal Ceramic Chai & Coffee Cups (Set of 6)",
                "slug": "avyro-artisanal-ceramic-chai-cups-set-of-6",
                "sku": "AVY-HK-009",
                "description": "Handcrafted terracotta glazed ceramic tea cups (180ml). Microwave and dishwasher safe, featuring traditional Indian studio pottery craftsmanship.",
                "short_description": "Handmade glazed ceramic tea & coffee kulhad cups set of 6.",
                "price": 1199.0,
                "sale_price": 799.0,
                "stock": 25,
                "category_id": get_cat("Cups & Mugs"),
                "brand": "AVYRO Home",
                "weight": "1.3kg",
                "dimensions": "180ml capacity each",
                "featured": True,
                "bestseller": True,
                "images": ["prod-cups-1.jpg"]
            },
            {
                "name": "AVYRO Multipurpose Refrigerator Storage Baskets (Set of 4)",
                "slug": "avyro-multipurpose-fridge-storage-baskets-4",
                "sku": "AVY-HK-010",
                "description": "Ventilated fridge organizer bins with built-in handle grooves. Keeps fruits, vegetables, and condiments organized and fresh.",
                "short_description": "Ventilated BPA-free fridge organizer bins with handles.",
                "price": 899.0,
                "sale_price": 549.0,
                "stock": 30,
                "category_id": get_cat("Refrigerator Organizers"),
                "brand": "AVYRO Home",
                "weight": "520g",
                "dimensions": "30 x 14 x 10 cm",
                "featured": False,
                "bestseller": True,
                "images": ["prod-fridgeracks-1.jpg"]
            }
        ]

        for pdata in products_data:
            imgs = pdata.pop("images")
            prod = Product(**pdata)
            db.session.add(prod)
            db.session.flush()

            for idx, img_file in enumerate(imgs):
                pimg = ProductImage(product_id=prod.id, image_path=img_file, sort_order=idx)
                db.session.add(pimg)

        # Seed Admin & Demo Customer
        if not User.query.filter_by(email='admin@avyro.com').first():
            admin = User(name='AVYRO Administrator', email='admin@avyro.com', is_admin=True)
            admin.set_password('Admin@123')
            db.session.add(admin)

        if not User.query.filter_by(email='user@avyro.com').first():
            user = User(name='Vikramaditya Sharma', email='user@avyro.com', is_admin=False, phone='+91 98765 43210')
            user.set_password('User@123')
            db.session.add(user)

        db.session.commit()

        print("==================================================")
        print("  AVYRO Seed Complete!")
        print("  Category Structure: Home & Kitchen Marketplace")
        print("  Admin Login: admin@avyro.com / Admin@123")
        print("  Customer Login: user@avyro.com / User@123")
        print(f"  Main Categories Seeded: {len(hk_structure)}")
        print(f"  Products Seeded: {len(products_data)}")
        print("==================================================")

if __name__ == '__main__':
    seed_database()
