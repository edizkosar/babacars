# BabaCars – Project Overview

## Stack
- **Backend:** Django 5.x + Django REST Framework
- **Frontend:** Tailwind CSS + GSAP
- **Database:** SQLite
- **Auth:** Django built-in auth + custom User model

## Architecture
**MTV + Service Layer**
- `models.py` → Data definition only. No business logic.
- `views.py` → HTTP only. No business logic. Calls services.
- `services.py` → All business logic lives here.
- `selectors.py` → All DB queries live here.
- `forms.py` → Validation only.
- `serializers.py` → DRF serialization only.
- `templates/` → Presentation only.

## Apps

| App | Responsibility |
|-----|---------------|
| `accounts` | User model, auth, seller profile, ratings |
| `listings` | Vehicle listings, photos, search, filter, compare |
| `offers` | Offer/counter-offer system for sale & rental |
| `bookings` | Rental booking & availability management |
| `messaging` | Conversation & message between users |
| `notifications` | In-app notification system |
| `dashboard` | Seller analytics (views, favorites, traffic) |
| `api` | DRF REST API endpoints |

## User Roles
- `buyer` → Browse, search, make offers, send messages, compare, book rentals
- `seller` → Create listings, manage offers, view dashboard, respond to messages
- `admin` → Django admin panel, full access

> A user can be both buyer and seller simultaneously.

## Listing Types
- `sale` → Vehicle for sale. Supports offer system.
- `rental` → Vehicle for rent. Supports booking + offer system.

## Core Features
1. Authentication (register, login, logout, profile)
2. Listings CRUD (create, edit, delete, detail, index)
3. Search & Filter (make, model, year, price, fuel, transmission)
4. Pagination (listings index, search results)
5. Offer System (offer → accept/reject/counter)
6. Booking System (rental date range, availability)
7. Comparison System (up to 3 vehicles side by side)
8. Messaging System (buyer ↔ seller per listing)
9. Notification System (in-app, triggered by offers/messages/bookings)
10. Seller Dashboard (analytics per listing)
11. Seller Profile & Rating (reviews, verified badge)
12. REST API (DRF – listings, offers, bookings)
13. AJAX (offers, messaging, favorites, compare)
14. Third-party API (to be defined – e.g. currency or map API)

## Model Relationships (High Level)

```
User ──< Listing (seller)
User ──< Offer (buyer)
User ──< Review (reviewer)
User ──< Message (sender)

Listing ──< Photo
Listing ──< Offer
Listing ──< Booking
Listing ──< Message (via Conversation)
Listing >── Vehicle (make, model, specs)

Offer ──< Offer (counter-offer chain, self-referential)

Conversation ──< Message
Conversation >── Listing
Conversation >── User (buyer)
Conversation >── User (seller)

Notification >── User (recipient)
```

## Naming Conventions
- Models: `PascalCase`
- Fields: `snake_case`
- URLs: `kebab-case`
- Template files: `snake_case.html`
- JS files: `camelCase.js`
- CSS files: `kebab-case.css`
- Services/Selectors functions: `verb_noun` (e.g. `create_offer`, `get_active_listings`)

## Frontend Principles
- Tailwind CSS utility classes only (no custom CSS unless unavoidable)
- GSAP for animations
- AJAX for: offer submission, messaging, favorite toggle, compare add/remove
- Mobile-first responsive design
- User-friendly: clear CTAs, loading states, error feedback, empty states

## Deployment
- **Platform:** Render
- **Database:** SQLite (persistent disk on Render)
- **Static files:** WhiteNoise
- **Environment variables:** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` via Render dashboard

## API Principles (DRF)
- Endpoint prefix: `/api/v1/`
- Auth: Session-based (same as web) + Token auth for external clients
- Format: JSON only

## File Structure
```
babacars/
├── babacars/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── forms.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── listings/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── forms.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── offers/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── forms.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── bookings/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── forms.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── messaging/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── notifications/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   ├── urls.py
│   └── admin.py
├── dashboard/
│   ├── views.py
│   ├── services.py
│   ├── selectors.py
│   └── urls.py
├── api/
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── listings/
│   ├── offers/
│   ├── bookings/
│   ├── messaging/
│   ├── notifications/
│   └── dashboard/
└── static/
    ├── css/
    ├── js/
    └── images/
```
