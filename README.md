# AVYRO — Modern Premium E-Commerce Platform

**AVYRO** is a full-featured, high-performance, and visually stunning e-commerce application built for selling physical products online. Engineered with Python Flask, SQLAlchemy, HTML5, Custom CSS design system with Bootstrap 5, and Vanilla JavaScript.

---

## Technical Stack & Architecture

- **Backend Framework**: Python Flask 3.x
- **Database & ORM**: SQLite (SQLAlchemy ORM) — easily convertible to PostgreSQL/MySQL via `DATABASE_URL`
- **Authentication**: Session-based auth with Werkzeug password hashing & `@login_required` / `@admin_required` decorators
- **Frontend Architecture**: HTML5, Jinja2 Template Inheritance, Custom CSS Design System with Bootstrap 5
- **Icons & Visuals**: Bootstrap Icons, Unsplash High-Res Product Assets
- **Client Interactions**: Vanilla JS (AJAX Cart, Wishlist toggles, Live Search Autocomplete, Image Gallery Switcher)
- **Analytics Charts**: Chart.js for Admin sales & revenue statistics

---

## Project Structure

```text
AVYRO/
├── app/
│   ├── __init__.py           # App Factory & Context Processors
│   ├── extensions.py         # SQLAlchemy & LoginManager
│   ├── models.py             # User, Product, Category, Cart, Order, Wishlist, Address
│   ├── auth/                 # Customer Registration, Login & Session Management
│   ├── shop/                 # Public Catalog, Product Details, Filters & Live Search API
│   ├── cart/                 # Dynamic AJAX Shopping Cart Operations
│   ├── orders/               # Checkout Flow & Order Processing
│   ├── account/              # User Profile, Addresses & Wishlist
│   ├── admin/                # Protected Admin Dashboard & Management CRUD
│   ├── static/
│   │   ├── css/styles.css    # Centralized Design System & Animations
│   │   ├── js/main.js        # Global Client Scripts & Toasts
│   │   ├── js/admin.js       # Admin Preview Scripts
│   │   └── uploads/          # Uploaded Product & Category Images
│   └── templates/            # Jinja2 Layout Templates & Views
├── config.py                 # Configuration Settings
├── seed.py                   # Automated Database Initializer & Demo Data Populator
├── run.py                    # Application Entry Point
├── requirements.txt          # Python Dependencies
├── .env.example              # Environment Configuration Template
└── README.md
```

---

## Default Credentials

### 1. Administrator Portal Access
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Email**: `admin@avyro.com`
- **Password**: `Admin@123`

### 2. Demo Customer Account
- **URL**: `http://127.0.0.1:5000/login`
- **Email**: `user@avyro.com`
- **Password**: `User@123`

> [!IMPORTANT]
> Change default passwords before deploying to a production environment.

---

## Quick Start Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed Database & Assets
Run the seed script to create database tables, seed demo categories, products, images, and user accounts:
```bash
python seed.py
```

### Step 3: Launch AVYRO Web Application
```bash
python run.py
```
Open your browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

---

## Key Features

### 1. Customer Panel
- **Homepage**: Sticky Glassmorphism Header, Hero Slider, Featured Categories, Trending & Bestsellers, Promotional Banners, Why Choose AVYRO Trust Cards, Newsletter.
- **Product Catalog**: Live search input with instant autocomplete suggestions dropdown, Category radio filter, Price range sliders, Availability toggle, Sorting options (Newest, Price Low/High, Popularity), Pagination.
- **Product Details**: Multi-image thumbnail gallery switcher, discount percentage calculation, live stock counter, technical specs tab, reviews ratings, related products slider.
- **Shopping Cart**: Real-time quantity increment/decrement, free shipping progress indicator, instant item removal, subtotal & grand total calculation.
- **Checkout & Order Placement**: Shipping address form with default address pre-filling, guest or account order creation, payment method selector (COD / Online Card).
- **Customer Dashboard**: Overview metrics, order status tracking timeline, saved shipping address manager, and saved wishlist items.

### 2. Admin Panel (`/admin`)
- **Protected Security**: Admin routes strictly check `@admin_required` privilege. Unauthorized users are blocked with HTTP 403 / redirect.
- **Analytics Dashboard**: 6 Stat Cards (Products, Customers, Orders, Revenue, Pending Orders, Low Stock Alert), Chart.js graphs for monthly revenue trends & category distribution, Recent Orders table.
- **Product CRUD**: Add/Edit products with multi-image file upload & live preview, automatic URL-friendly slug generator, stock quantity updater, featured/bestseller badges. Delete with confirmation modal.
- **Category Management**: Create/Edit categories with cover photos.
- **Order Lifecycle Management**: View order details, update payment status & order fulfillment status (`Pending` → `Processing` → `Shipped` → `Delivered` → `Cancelled`).
- **Customer Directory**: View customer list with registration dates, order counts, and total spent metrics.

---

## Future Expansion Architecture

The application is structured for easy integration with:
- **Payment Gateways**: Extensible checkout flow prepared for Razorpay / Stripe SDKs in `app/orders/routes.py`.
- **Email Notifications**: Integration points for Flask-Mail / SendGrid order confirmation emails.
- **Tax & Shipping APIs**: Modular price calculation functions ready for GST invoice generation and courier tracking APIs (Shiprocket / Delhivery).
