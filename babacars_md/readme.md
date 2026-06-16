# readme.md

## Purpose
Project README for submission. Worth 6 pts in rubric.
Clear, professional, covers all required sections.

---

## README.md (to be placed in project root)

```markdown
# BabaCars 🚗

A modern vehicle listing and rental platform built with Django.
Buy, sell, and rent vehicles with a seamless offer-based negotiation system.

---

## Features

- 🔐 **Authentication** — Register, login, email verification
- 🚘 **Listings** — Create, edit, search and filter vehicle listings
- 💰 **Offer System** — Negotiate price with counter-offer chains
- 📅 **Booking System** — Rental bookings via accepted offers
- 💬 **Messaging** — Direct messaging between buyers and sellers
- 🔔 **Notifications** — Real-time in-app notification system
- 📊 **Seller Dashboard** — Analytics, traffic and offer stats
- ⭐ **Seller Profiles** — Ratings, reviews and verified badges
- 🔄 **Comparison** — Compare up to 3 vehicles side by side
- 🌐 **REST API** — Full DRF API with token authentication

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x |
| API | Django REST Framework |
| Frontend | Tailwind CSS + GSAP |
| Database | SQLite |
| Deployment | Render |
| Static Files | WhiteNoise |

---

## Architecture

MTV + Service Layer pattern:

```
models.py     → Data definition
services.py   → Business logic
selectors.py  → Database queries
views.py      → HTTP layer
templates/    → Presentation
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<username>/babacars.git
cd babacars
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run development server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | insecure default |
| `DEBUG` | Debug mode | True |
| `ALLOWED_HOSTS` | Allowed hostnames | localhost 127.0.0.1 |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/v1/listings/ | Public | List active listings |
| GET | /api/v1/listings/<slug>/ | Public | Listing detail |
| GET | /api/v1/offers/ | Required | My offers |
| GET | /api/v1/bookings/ | Required | My bookings |
| GET | /api/v1/listings/<id>/unavailable-dates/ | Public | Unavailable dates |

---

## Models

| Model | App | Description |
|-------|-----|-------------|
| User | accounts | Custom user with role |
| SellerProfile | accounts | Seller info and rating |
| Review | accounts | Buyer reviews for sellers |
| Listing | listings | Vehicle listing |
| Vehicle | listings | Vehicle specs |
| Photo | listings | Listing photos |
| Favorite | listings | User favorites |
| ListingView | listings | View tracking |
| Offer | offers | Offer/counter-offer chain |
| Booking | bookings | Rental booking |
| UnavailableDate | bookings | Blocked dates |
| Conversation | messaging | Buyer-seller conversation |
| Message | messaging | Individual message |
| Notification | notifications | In-app notification |

---

## Deployment

Live URL: https://babacars.onrender.com

Deployed on Render with:
- SQLite persistent disk
- WhiteNoise for static files
- Environment variables via Render dashboard
```

---

## PROMPT

### Task
Create README.md in the project root exactly as defined above.

### Rules
1. Copy markdown content exactly.
2. Update GitHub URL with actual repository URL.
3. Update live Render URL once deployed.
4. Do NOT add or remove sections.

### Output
Single README.md file. No explanations.
