# dashboard/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See listings_models.md for Listing, ListingView, Favorite models.
See offers_models.md for Offer model.
See bookings_models.md for Booking model.
See messaging_models.md for Conversation model.

## Purpose
Aggregates analytics data for seller dashboard.
No HTTP logic. No model creation. Read-only. Calls selectors.py for data access.

## Dependencies
```python
from django.utils import timezone
from datetime import timedelta
from dashboard import selectors
```

## Functions

---

### get_dashboard_summary
```python
def get_dashboard_summary(*, user) -> dict:
```
- Raises PermissionError if user.is_seller() is False
- Calls all stat functions below and returns combined dict
- Returns:
```python
{
    'total_listings': int,
    'active_listings': int,
    'total_views': int,
    'total_favorites': int,
    'total_offers': int,
    'pending_offers': int,
    'total_bookings': int,
    'active_bookings': int,
    'unread_messages': int,
}
```

---

### get_listing_stats
```python
def get_listing_stats(*, user, listing_id: int) -> dict:
```
- Fetches listing via listings.selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Returns:
```python
{
    'view_count': int,
    'favorite_count': int,
    'offer_count': int,
    'pending_offer_count': int,
    'message_count': int,
    'hourly_traffic': list,   # last 7 days, grouped by hour
    'daily_traffic': list,    # last 30 days, grouped by day
}
```

---

### get_hourly_traffic
```python
def get_hourly_traffic(*, listing_id: int, days: int = 7) -> list:
```
- Fetches ListingView records for listing within last `days` days
- Groups by hour of day (0–23)
- Returns list of 24 dicts: [{'hour': 0, 'count': int}, ...]
- Called from get_listing_stats only

---

### get_daily_traffic
```python
def get_daily_traffic(*, listing_id: int, days: int = 30) -> list:
```
- Fetches ListingView records for listing within last `days` days
- Groups by date
- Returns list of dicts: [{'date': str, 'count': int}, ...]
- Called from get_listing_stats only

---

### get_offer_conversion_rate
```python
def get_offer_conversion_rate(*, listing_id: int) -> float:
```
- Fetches total offer count and accepted offer count for listing
- Returns accepted / total as float (0.0 if no offers)
- Called from get_listing_stats only

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test dashboard.tests.test_services
```
Manually verify:
- get_dashboard_summary raises PermissionError for non-seller
- get_hourly_traffic returns list of 24 items
- get_daily_traffic returns correct date range
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
