# bookings/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See bookings_models.md for Booking, UnavailableDate models and booking logic.
See offers_models.md for Offer model.
See listings_models.md for Listing model.

## Purpose
All business logic for booking creation, confirmation, cancellation and availability checking.
Bookings can only be created via an accepted offer. No direct booking.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.utils import timezone
from bookings.models import Booking, UnavailableDate
from bookings import selectors
from notifications.services import create_notification
```

## Functions

---

### create_booking_from_offer
```python
def create_booking_from_offer(*, offer) -> Booking:
```
- Called only from offers/services.py after offer accepted
- Raises ValueError if offer.listing.listing_type != 'rental'
- Raises ValueError if date range is no longer available (calls check_availability)
- Calculates total_price from offer.amount
- Creates Booking with status='confirmed'
- Creates UnavailableDate for the booked date range with reason='booked'
- Sets listing.status = 'rented'
- Calls create_notification for renter → type='booking_confirmed'
- Returns created Booking

---

### cancel_booking
```python
def cancel_booking(*, user, booking_id: int) -> Booking:
```
- Fetches booking via selectors.get_booking_by_id
- Raises PermissionError if user != booking.renter and user != booking.listing.seller
- Raises ValueError if booking.status == 'completed'
- Sets booking.status = 'cancelled'
- Deletes corresponding UnavailableDate for this booking's date range
- Sets listing.status = 'active'
- Calls create_notification for both renter and seller → type='booking_cancelled'
- Returns updated booking

---

### complete_booking
```python
def complete_booking(*, booking_id: int) -> Booking:
```
- Fetches booking via selectors.get_booking_by_id
- Raises ValueError if booking.status != 'active'
- Sets booking.status = 'completed'
- Sets listing.status = 'active'
- Returns updated booking
- Note: Called from middleware when booking.end_date < today

---

### check_availability
```python
def check_availability(*, listing_id: int, start_date, end_date) -> bool:
```
- Fetches all UnavailableDate records for listing (calls selectors.get_unavailable_dates)
- Returns False if any unavailable range overlaps with requested start_date–end_date
- Overlap condition: start_date < unavailable.end_date AND end_date > unavailable.start_date
- Returns True if no overlap found

---

### block_dates
```python
def block_dates(*, user, listing_id: int, start_date, end_date, reason: str = 'blocked') -> UnavailableDate:
```
- Fetches listing via listings.selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Raises ValueError if reason not in ['maintenance', 'blocked']
- Raises ValueError if date range overlaps with existing UnavailableDate (calls check_availability)
- Creates and returns UnavailableDate

---

### unblock_dates
```python
def unblock_dates(*, user, unavailable_date_id: int) -> None:
```
- Fetches UnavailableDate via selectors.get_unavailable_date_by_id
- Raises PermissionError if user != unavailable_date.listing.seller
- Raises ValueError if unavailable_date.reason == 'booked' (cannot unblock a confirmed booking)
- Deletes UnavailableDate

---

### calculate_total_price
```python
def calculate_total_price(*, offer) -> float:
```
- Calculates duration_days = (offer.rental_end_date - offer.rental_start_date).days
- Applies discount rules:
    - 1–6 days    → offer.listing.price × duration_days
    - 7–29 days   → offer.listing.price × duration_days × 0.90
    - 30–364 days → offer.listing.price × duration_days × 0.80
    - 365+ days   → offer.listing.price × duration_days × 0.70
- Returns total_price as float
- Internal function. Called from create_booking_from_offer only.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test bookings.tests.test_services
```
Manually verify:
- create_booking_from_offer creates UnavailableDate automatically
- cancel_booking deletes corresponding UnavailableDate
- check_availability returns False on overlapping dates
- calculate_total_price applies correct discount tier
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
