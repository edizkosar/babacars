# bookings/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User model.
See listings_models.md for Listing model.
See offers_models.md for Offer model.

## Purpose
Rental booking management and availability tracking.
Only applicable to listings with listing_type='rental'.

## Dependencies
```python
from django.db import models
from django.conf import settings
```

## Models

---

### Booking
Represents a confirmed rental reservation.

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='bookings' |
| `renter` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='bookings' |
| `offer` | OneToOneField | Offer, on_delete=SET_NULL, null=True, blank=True, related_name='booking' |
| `start_date` | DateField | |
| `end_date` | DateField | |
| `total_price` | DecimalField | max_digits=12, decimal_places=2 |
| `currency` | CharField | max_length=3, default='TRY' |
| `status` | CharField | choices=STATUS_CHOICES, max_length=20, default='pending' |
| `note` | TextField | blank=True |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**STATUS_CHOICES**
```python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]
```

**Meta**
```python
class Meta:
    db_table = 'bookings'
    ordering = ['-created_at']
    verbose_name = 'Booking'
    verbose_name_plural = 'Bookings'
```

**Methods**
```python
def duration_days(self) -> int:
    return (self.end_date - self.start_date).days

def __str__(self) -> str:
    return f"Booking({self.renter.email} → {self.listing.title} | {self.start_date} – {self.end_date})"
```

---

### UnavailableDate
Marks specific date ranges as unavailable for a rental listing.
Used to block dates after confirmed bookings or seller manual blocks.

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='unavailable_dates' |
| `start_date` | DateField | |
| `end_date` | DateField | |
| `reason` | CharField | choices=REASON_CHOICES, max_length=20, default='booked' |
| `created_at` | DateTimeField | auto_now_add=True |

**REASON_CHOICES**
```python
REASON_CHOICES = [
    ('booked', 'Booked'),
    ('maintenance', 'Maintenance'),
    ('blocked', 'Blocked by Seller'),
]
```

**Meta**
```python
class Meta:
    db_table = 'unavailable_dates'
    verbose_name = 'Unavailable Date'
    verbose_name_plural = 'Unavailable Dates'
```

**Methods**
```python
def __str__(self) -> str:
    return f"Unavailable({self.listing.title} | {self.start_date} – {self.end_date})"
```

---

## Booking Logic
> AI must not implement this logic in models.py.
> All booking logic lives in bookings/services.py.

```
Rules:
- Booking can only be created for listing_type='rental'.
- start_date must be today or in the future.
- end_date must be after start_date.
- Requested date range must not overlap with any UnavailableDate for the same listing.
- On booking confirmed → UnavailableDate created automatically for that date range with reason='booked'.
- On booking cancelled → corresponding UnavailableDate deleted.
- total_price calculated in services.py using duration_days:
    - 1–6 days   → listing.price × duration_days (daily rate)
    - 7–29 days  → listing.price × duration_days × 0.90 (10% weekly discount)
    - 30–364 days → listing.price × duration_days × 0.80 (20% monthly discount)
    - 365+ days  → listing.price × duration_days × 0.70 (30% yearly discount)
- If booking created from an accepted offer → total_price taken from offer.amount, discount rules do not apply.
- On offer accepted → Booking created automatically in services.py.
- On booking created from accepted offer → listing.status set to 'rented'.
- All other pending/countered offers on same listing → status set to 'cancelled' automatically.
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations bookings --check
python manage.py test bookings
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
