# offers/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See offers_models.md for Offer model and chain logic.
See listings_models.md for Listing model.
See accounts_models.md for User model.

## Purpose
All business logic for offer creation, counter-offers, acceptance, rejection and expiry.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.utils import timezone
from datetime import timedelta
from offers.models import Offer
from offers import selectors
from notifications.services import create_notification
```

## Functions

---

### create_offer
```python
def create_offer(*, buyer, listing_id: int, amount: float, message: str = '', rental_start_date=None, rental_end_date=None) -> Offer:
```
- Fetches listing via listings.selectors.get_listing_by_id
- Raises ValueError if listing.status not in ['active']
- Raises PermissionError if buyer == listing.seller
- Raises ValueError if listing.listing_type == 'rental' and rental_start_date or rental_end_date is None
- Raises ValueError if rental_end_date <= rental_start_date
- Raises ValueError if buyer already has a pending offer on this listing (calls selectors.get_pending_offer)
- Raises ValueError if amount <= 0
- Sets expires_at = timezone.now() + timedelta(days=30)
- Creates and returns Offer with parent_offer=None
- Calls create_notification for seller → type='new_offer'

---

### accept_offer
```python
def accept_offer(*, user, offer_id: int) -> Offer:
```
- Fetches offer via selectors.get_offer_by_id
- Raises PermissionError if user != offer.listing.seller
- Raises ValueError if offer.status != 'pending'
- Sets offer.status = 'accepted'
- Cancels all other pending/countered offers on same listing via cancel_other_offers()
- If listing.listing_type == 'rental' → calls bookings.services.create_booking_from_offer()
- If listing.listing_type == 'sale' → sets listing.status = 'sold'
- Calls create_notification for buyer → type='offer_accepted'
- Returns updated offer

---

### reject_offer
```python
def reject_offer(*, user, offer_id: int) -> Offer:
```
- Fetches offer via selectors.get_offer_by_id
- Raises PermissionError if user != offer.listing.seller
- Raises ValueError if offer.status != 'pending'
- Sets offer.status = 'rejected'
- Calls create_notification for buyer → type='offer_rejected'
- Returns updated offer

---

### counter_offer
```python
def counter_offer(*, user, offer_id: int, amount: float, message: str = '') -> Offer:
```
- Fetches offer via selectors.get_offer_by_id
- Raises PermissionError if user != offer.listing.seller
- Raises ValueError if offer.status != 'pending'
- Raises ValueError if amount <= 0
- Sets current offer.status = 'countered'
- Creates new Offer with parent_offer=current offer, buyer=current offer.buyer
- Sets expires_at = timezone.now() + timedelta(days=30)
- Calls create_notification for buyer → type='offer_countered'
- Returns new counter offer

---

### cancel_offer
```python
def cancel_offer(*, user, offer_id: int) -> Offer:
```
- Fetches offer via selectors.get_offer_by_id
- Raises PermissionError if user != offer.buyer
- Raises ValueError if offer.status != 'pending'
- Sets offer.status = 'cancelled'
- Returns updated offer

---

### expire_stale_offers
```python
def expire_stale_offers() -> int:
```
- Fetches all pending offers where expires_at <= timezone.now() (calls selectors.get_expired_offers)
- Sets each offer.status = 'expired'
- Calls create_notification for buyer and seller → type='offer_expired'
- Returns count of expired offers
- Note: Called periodically (e.g. on every request via middleware or management command)

---

### cancel_other_offers
```python
def cancel_other_offers(*, listing, exclude_offer_id: int) -> None:
```
- Fetches all pending and countered offers on listing excluding exclude_offer_id
- Sets each offer.status = 'cancelled'
- Internal function. Not called from views directly.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test offers.tests.test_services
```
Manually verify:
- create_offer raises PermissionError if buyer == seller
- create_offer raises ValueError if buyer has existing pending offer
- accept_offer cancels all other pending offers on same listing
- counter_offer sets parent offer status to 'countered'
- expire_stale_offers sets expired offers to 'expired'
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
