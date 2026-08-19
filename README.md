# Marketplace - Product Listing and Sales Website

A production-ready Django website for listing and selling items. Features an admin panel for managing listings, Cloudinary image hosting, WhatsApp-based purchase flow, and automatic cleanup of sold listings.

---

## Features

### Customer Side
- Browse available products with photos
- Filter by category, type, and sort by price
- WhatsApp and Call buttons on every listing
- Detailed item profile pages (condition, price, location, documentation, status)
- Pop-up lead capture modal
- Customer testimonial carousel
- Mobile-first responsive design with sticky contact bar

### Admin Side
- Add, edit, and delete product listings from the Django admin panel
- Upload multiple photos per item (stored securely on Cloudinary)
- Mark items as Sold, Reserved, or Available
- Inline price and status editing
- Manage customer testimonials
- Site-wide configuration (WhatsApp number, hero text, and pop-up settings)
- Automatic cleanup of sold product listings and associated Cloudinary images

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | Django 5.1 |
| Database | PostgreSQL 16 |
| Image Hosting | Cloudinary (Free Tier) |
| CSS Framework | Tailwind CSS (CDN) |
| Icons | Font Awesome 6 |
| Carousel | Swiper.js |
| Static Files | WhiteNoise |
| Web Server | Gunicorn + Nginx |
| Containerization | Docker |
| WhatsApp Integration | wa.me deep links (No API required) |

---

## Project Structure

```text
marketplace/
├── config/                         # Django project configuration
│   ├── settings.py                 # Main settings (Database, Cloudinary, etc.)
│   ├── urls.py                     # Root URL routing
│   └── wsgi.py                     # WSGI entry point
├── apps/
│   └── items/                      # Main application
│       ├── models.py               # Item, Category, ItemImage, Testimonial, SiteConfig
│       ├── admin.py                # Admin panel configuration
│       ├── views.py                # Home page + Item detail views
│       ├── urls.py                 # URL routing
│       ├── context_processors.py   # Global site config context
│       ├── templatetags/
│       │   └── item_tags.py        # WhatsApp URL + star rating tags
│       └── management/
│           └── commands/
│               └── cleanup_sold_items.py # Auto-delete sold items and images
├── templates/
│   ├── base.html                   # Master layout (header, footer, modal, sticky bar)
│   ├── home.html                   # Landing page
│   └── items/
│       └── detail.html             # Single item detail page
├── static/
│   └── css/
│       └── custom.css              # Custom styles
├── docker-compose.yml              # Development database (PostgreSQL)
├── docker-compose.prod.yml         # Production deployment
├── Dockerfile                      # Production container
├── nginx/
│   └── nginx.conf                  # Reverse proxy configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (Excluded from source control)
├── .env.example                    # Template for environment variables
└── .gitignore                      # Git ignore rules
```

---

## Quick Start (Development)

### Prerequisites
- Python 3.12+
- PostgreSQL 16 (or Docker)
- Cloudinary account

### 1. Clone the repository
```bash
git clone https://github.com
cd marketplace
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and supply your local values:
# - SECRET_KEY (Generate a random 50+ character string)
# - Database credentials
# - Cloudinary credentials
# - Admin WhatsApp number
```

### 5. Start the database

#### Option A - Docker:
```bash
docker compose up -d
```

#### Option B - Local PostgreSQL:
```sql
-- In psql command line:
CREATE DATABASE marketplace;
```

### 6. Run migrations
```bash
python manage.py makemigrations items
python manage.py migrate
```

### 7. Create admin account
```bash
python manage.py createsuperuser
```

### 8. Run the server
```bash
python manage.py runserver
```

### 9. Open in browser
- Website: `http://127.0.0`
- Admin Panel: `http://127.0.0secretadmin/`

### 10. Initial setup in admin panel
1. Navigate to Site Configuration and complete fields for the WhatsApp number, phone, and hero text.
2. Navigate to Categories and populate required classes (e.g., Electronics, Apparel, Home Goods).
3. Navigate to Items to establish your first product listing with accompanying photos.
4. Navigate to Testimonials to document verified user reviews.

---

## Database Schema

```text
categories ──1:N──> items ──1:N──> item_images
                  
testimonials (standalone)
site_config  (singleton — 1 row only)
```
