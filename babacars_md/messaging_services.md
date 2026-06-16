# messaging/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See messaging_models.md for Conversation, Message models.
See listings_models.md for Listing model.

## Purpose
All business logic for conversation and message management between buyer and seller.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.utils import timezone
from messaging.models import Conversation, Message
from messaging import selectors
from notifications.services import create_notification
```

## Functions

---

### get_or_create_conversation
```python
def get_or_create_conversation(*, buyer, listing_id: int) -> Conversation:
```
- Fetches listing via listings.selectors.get_listing_by_id
- Raises ValueError if listing.status not in ['active']
- Raises PermissionError if buyer == listing.seller
- Returns existing Conversation if found (calls selectors.get_conversation)
- Creates and returns new Conversation if not found

---

### send_message
```python
def send_message(*, sender, conversation_id: int, body: str) -> Message:
```
- Fetches conversation via selectors.get_conversation_by_id
- Raises PermissionError if sender not in [conversation.buyer, conversation.seller]
- Raises ValueError if body is empty or whitespace only
- Raises ValueError if conversation.is_active is False
- Creates Message
- Updates conversation.updated_at (auto_now handles this)
- Calls create_notification for recipient → type='new_message'
- Returns created Message

---

### mark_messages_as_read
```python
def mark_messages_as_read(*, user, conversation_id: int) -> int:
```
- Fetches conversation via selectors.get_conversation_by_id
- Raises PermissionError if user not in [conversation.buyer, conversation.seller]
- Fetches all unread messages where sender != user (calls selectors.get_unread_messages)
- Sets is_read=True, read_at=timezone.now() on all fetched messages
- Returns count of marked messages

---

### delete_message
```python
def delete_message(*, user, message_id: int) -> Message:
```
- Fetches message via selectors.get_message_by_id
- Raises PermissionError if user != message.sender
- Raises ValueError if message.is_deleted is True
- Sets message.body = 'Bu mesaj silindi.'
- Sets message.is_deleted = True
- Returns updated message

---

### close_conversation
```python
def close_conversation(*, user, conversation_id: int) -> Conversation:
```
- Fetches conversation via selectors.get_conversation_by_id
- Raises PermissionError if user not in [conversation.buyer, conversation.seller]
- Sets conversation.is_active = False
- Returns updated conversation

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test messaging.tests.test_services
```
Manually verify:
- get_or_create_conversation raises PermissionError if buyer == seller
- send_message raises ValueError if body is empty
- delete_message sets body to 'Bu mesaj silindi.' and is_deleted=True
- mark_messages_as_read only marks messages not sent by user
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
