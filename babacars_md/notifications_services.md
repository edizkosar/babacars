# notifications/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See notifications_models.md for Notification model and trigger map.

## Purpose
All business logic for notification creation and management.
Called from other apps' services.py files. Never called from views directly.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.utils import timezone
from notifications.models import Notification
from notifications import selectors
from django.contrib.contenttypes.models import ContentType
```

## Functions

---

### create_notification
```python
def create_notification(*, recipient, notification_type: str, title: str, body: str = '', related_object=None) -> Notification:
```
- Raises ValueError if notification_type not in TYPE_CHOICES
- Raises ValueError if recipient == None
- If related_object provided → resolves content_type and object_id via ContentType
- Creates and returns Notification

---

### mark_as_read
```python
def mark_as_read(*, user, notification_id: int) -> Notification:
```
- Fetches notification via selectors.get_notification_by_id
- Raises PermissionError if user != notification.recipient
- Raises ValueError if notification.is_read is True
- Sets notification.is_read = True, read_at = timezone.now()
- Returns updated notification

---

### mark_all_as_read
```python
def mark_all_as_read(*, user) -> int:
```
- Fetches all unread notifications for user (calls selectors.get_unread_notifications)
- Bulk updates is_read=True, read_at=timezone.now()
- Returns count of marked notifications

---

### get_unread_count
```python
def get_unread_count(*, user) -> int:
```
- Calls selectors.get_unread_notifications
- Returns count as int
- Used by navbar AJAX to display unread badge

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test notifications.tests.test_services
```
Manually verify:
- create_notification raises ValueError for invalid notification_type
- mark_all_as_read returns correct count
- get_unread_count returns 0 for user with no notifications
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
