# listings/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See listings_models.md for Listing, Vehicle, Photo, Favorite, ListingView models.

## Purpose
All business logic for listing creation, update, deletion, favorites and view tracking.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.utils.text import slugify
from django.utils import timezone
from listings.models import Listing, Vehicle, Photo, Favorite, ListingView
from listings import selectors
```

## Functions

---

### create_listing
```python
def create_listing(*, seller, listing_data: dict, vehicle_data: dict, photos: list) -> Listing:
```
- Raises PermissionError if seller.is_seller() is False
- Raises ValueError if len(photos) < 8
- Creates Listing from listing_data
- Creates Vehicle from vehicle_data linked to listing
- Creates Photo objects for each photo, sets first as is_cover=True
- Returns created Listing

---

### update_listing
```python
def update_listing(*, user, listing_id: int, listing_data: dict = None, vehicle_data: dict = None) -> Listing:
```
- Fetches listing via selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Raises ValueError if listing.status in ['sold', 'rented']
- Updates Listing fields if listing_data provided
- Updates Vehicle fields if vehicle_data provided
- Returns updated Listing

---

### delete_listing
```python
def delete_listing(*, user, listing_id: int) -> None:
```
- Fetches listing via selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Raises ValueError if listing.status in ['sold', 'rented'] (active booking/sale exists)
- Deletes listing (cascades to Vehicle, Photo, Favorite, ListingView)

---

### set_listing_status
```python
def set_listing_status(*, user, listing_id: int, status: str) -> Listing:
```
- Fetches listing via selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Validates status is in STATUS_CHOICES
- Updates and returns listing

---

### add_photo
```python
def add_photo(*, user, listing_id: int, image) -> Photo:
```
- Fetches listing via selectors.get_listing_by_id
- Raises PermissionError if user != listing.seller
- Creates and returns Photo

---

### delete_photo
```python
def delete_photo(*, user, photo_id: int) -> None:
```
- Fetches photo via selectors.get_photo_by_id
- Raises PermissionError if user != photo.listing.seller
- Raises ValueError if photo.is_cover (cannot delete cover photo)
- Deletes photo

---

### set_cover_photo
```python
def set_cover_photo(*, user, photo_id: int) -> Photo:
```
- Fetches photo via selectors.get_photo_by_id
- Raises PermissionError if user != photo.listing.seller
- Sets all other photos of same listing is_cover=False
- Sets this photo is_cover=True
- Returns updated photo

---

### toggle_favorite
```python
def toggle_favorite(*, user, listing_id: int) -> dict:
```
- Fetches listing via selectors.get_listing_by_id
- Raises ValueError if user == listing.seller (cannot favorite own listing)
- If Favorite exists → delete it, decrement listing.favorite_count
- If Favorite does not exist → create it, increment listing.favorite_count
- Returns {'is_favorited': bool, 'favorite_count': int}

---

### track_view
```python
def track_view(*, listing_id: int, user=None, ip_address: str = None) -> None:
```
- Fetches listing via selectors.get_listing_by_id
- Creates ListingView with user (if authenticated) and ip_address
- Increments listing.view_count

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test listings.tests.test_services
```
Manually verify:
- create_listing raises ValueError if photos < 8
- create_listing raises PermissionError if user is not seller
- toggle_favorite returns correct is_favorited and favorite_count
- delete_photo raises ValueError if photo is cover
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
