# messaging/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User model.
See listings_models.md for Listing model.

## Purpose
Conversation and message management between buyer and seller per listing.
No real-time (no WebSockets). Standard request/response with AJAX polling.

## Dependencies
```python
from django.db import models
from django.conf import settings
```

## Models

---

### Conversation
One conversation per buyer–seller–listing combination.

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='conversations' |
| `buyer` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='buyer_conversations' |
| `seller` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='seller_conversations' |
| `is_active` | BooleanField | default=True |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**Meta**
```python
class Meta:
    db_table = 'conversations'
    unique_together = ('listing', 'buyer', 'seller')
    ordering = ['-updated_at']
    verbose_name = 'Conversation'
    verbose_name_plural = 'Conversations'
```

**Methods**
```python
def get_other_participant(self, user) -> object:
    return self.seller if user == self.buyer else self.buyer

def __str__(self) -> str:
    return f"Conversation({self.buyer.email} ↔ {self.seller.email} | {self.listing.title})"
```

---

### Message
Single message inside a conversation.

| Field | Type | Options |
|-------|------|---------|
| `conversation` | ForeignKey | Conversation, on_delete=CASCADE, related_name='messages' |
| `sender` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='sent_messages' |
| `body` | TextField | |
| `is_read` | BooleanField | default=False |
| `read_at` | DateTimeField | null=True, blank=True |
| `is_deleted` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |

**Meta**
```python
class Meta:
    db_table = 'messages'
    ordering = ['created_at']
    verbose_name = 'Message'
    verbose_name_plural = 'Messages'
```

**Methods**
```python
def __str__(self) -> str:
    return f"Message({self.sender.email} | {self.created_at:%Y-%m-%d %H:%M})"
```

---

## Messaging Logic
> AI must not implement this logic in models.py.
> All messaging logic lives in messaging/services.py.

```
Rules:
- Only one conversation per buyer–seller–listing combination.
- Seller cannot initiate a conversation. Only buyer can start.
- On new message sent → Conversation.updated_at refreshed automatically (auto_now=True).
- On message read → is_read=True, read_at=timezone.now() set in services.py.
- Sender can delete their own message → body replaced with 'Bu mesaj silindi.', is_deleted set to True in services.py.
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations messaging --check
python manage.py test messaging
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
