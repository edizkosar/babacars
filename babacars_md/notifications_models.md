# notifications/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User model.

## Purpose
In-app notification system. Triggered by offers, bookings, and messages.
No email or push notifications. In-app only.

## Dependencies
```python
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
```

## Models

---

### Notification
Single in-app notification for a user.

| Field | Type | Options |
|-------|------|---------|
| `recipient` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='notifications' |
| `notification_type` | CharField | choices=TYPE_CHOICES, max_length=30 |
| `title` | CharField | max_length=255 |
| `body` | TextField | blank=True |
| `is_read` | BooleanField | default=False |
| `read_at` | DateTimeField | null=True, blank=True |
| `content_type` | ForeignKey | ContentType, on_delete=CASCADE, null=True, blank=True |
| `object_id` | PositiveIntegerField | null=True, blank=True |
| `related_object` | GenericForeignKey | 'content_type', 'object_id' |
| `created_at` | DateTimeField | auto_now_add=True |

**TYPE_CHOICES**
```python
TYPE_CHOICES = [
    ('new_offer', 'New Offer'),
    ('offer_accepted', 'Offer Accepted'),
    ('offer_rejected', 'Offer Rejected'),
    ('offer_countered', 'Offer Countered'),
    ('offer_expired', 'Offer Expired'),
    ('new_message', 'New Message'),
    ('booking_confirmed', 'Booking Confirmed'),
    ('booking_cancelled', 'Booking Cancelled'),
    ('review_received', 'Review Received'),
]
```

**Meta**
```python
class Meta:
    db_table = 'notifications'
    ordering = ['-created_at']
    verbose_name = 'Notification'
    verbose_name_plural = 'Notifications'
```

**Methods**
```python
def mark_as_read(self):
    # Called from services.py only
    pass

def __str__(self) -> str:
    return f"Notification({self.recipient.email} | {self.notification_type})"
```

---

## Notification Trigger Map
> AI must not implement triggers in models.py.
> All trigger logic lives in respective app services.py files.

| Event | Trigger Location | Recipient |
|-------|-----------------|-----------|
| Buyer sends offer | offers/services.py | Seller |
| Seller accepts offer | offers/services.py | Buyer |
| Seller rejects offer | offers/services.py | Buyer |
| Seller counters offer | offers/services.py | Buyer |
| Offer expires | offers/services.py | Buyer + Seller |
| Buyer sends message | messaging/services.py | Seller |
| Seller sends message | messaging/services.py | Buyer |
| Booking confirmed | bookings/services.py | Buyer |
| Booking cancelled | bookings/services.py | Buyer + Seller |
| Review received | accounts/services.py | Seller |

## Notification Logic
> All logic lives in notifications/services.py.

```
Rules:
- Notification created via create_notification() in notifications/services.py.
- All other services import and call create_notification() — never create Notification directly.
- On mark as read → is_read=True, read_at=timezone.now().
- Mark all as read supported (bulk update).
- Unread count displayed in navbar via AJAX.
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations notifications --check
python manage.py test notifications
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
