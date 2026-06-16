# offers/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User model.
See listings_models.md for Listing model.

## Purpose
Offer, counter-offer chain management for both sale and rental listings.

## Dependencies
```python
from django.db import models
from django.conf import settings
```

## Models

---

### Offer
Represents a single offer in a negotiation chain.
Supports both sale (price) and rental (price + date range).

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='offers' |
| `buyer` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='sent_offers' |
| `parent_offer` | ForeignKey | 'self', on_delete=CASCADE, null=True, blank=True, related_name='counter_offers' |
| `amount` | DecimalField | max_digits=12, decimal_places=2 |
| `currency` | CharField | max_length=3, default='TRY' |
| `status` | CharField | choices=STATUS_CHOICES, max_length=20, default='pending' |
| `message` | TextField | blank=True |
| `rental_start_date` | DateField | null=True, blank=True |
| `rental_end_date` | DateField | null=True, blank=True |
| `expires_at` | DateTimeField | null=True, blank=True |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**STATUS_CHOICES**
```python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('countered', 'Countered'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]
```

**Meta**
```python
class Meta:
    db_table = 'offers'
    ordering = ['-created_at']
    verbose_name = 'Offer'
    verbose_name_plural = 'Offers'
```

**Methods**
```python
def is_rental_offer(self) -> bool:
    return self.rental_start_date is not None

def is_root_offer(self) -> bool:
    return self.parent_offer is None

def get_chain(self):
    # Returns full offer chain from root to this offer
    chain = []
    current = self
    while current is not None:
        chain.append(current)
        current = current.parent_offer
    return list(reversed(chain))

def __str__(self) -> str:
    return f"Offer({self.buyer.email} → {self.listing.title} | {self.amount} {self.currency})"
```

---

## Offer Chain Logic
> AI must not implement this logic in models.py.
> All chain logic lives in offers/services.py.

```
Initial offer (parent_offer=None)
    └── Counter offer (parent_offer=initial)
            └── Counter offer (parent_offer=previous counter)
                    └── ...

Rules:
- Only one pending offer per buyer per listing at a time.
- When seller counters → current offer status = 'countered', new offer created with parent_offer set.
- When offer accepted → all other pending offers on same listing = 'cancelled'.
- Rental offers must have both rental_start_date and rental_end_date.
- rental_end_date must be after rental_start_date.
- expires_at is set automatically to created_at + 30 days in services.py.
- Expired offers are caught and updated to 'expired' status in services.py.
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations offers --check
python manage.py test offers
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
