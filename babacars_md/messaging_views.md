# messaging/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See messaging_models.md for Conversation, Message models.
See messaging_services.md for all business logic.
See selectors.md → messaging/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
Message sending and reading use AJAX. Conversation list uses standard render.

## Dependencies
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from messaging import services, selectors
from messaging.forms import MessageForm
```

## Views

---

### inbox_view
```python
@login_required
@require_http_methods(["GET"])
def inbox_view(request):
```
- GET → fetch conversations via selectors.get_conversations_by_user(user=request.user)
- render 'messaging/inbox.html'

---

### conversation_view
```python
@login_required
@require_http_methods(["GET"])
def conversation_view(request, conversation_id):
```
- GET → fetch conversation via selectors.get_conversation_by_id
  - PermissionError if request.user not in [conversation.buyer, conversation.seller]
  - → redirect to 'messaging:inbox' with error message
- fetch messages via selectors.get_messages_by_conversation
- call services.mark_messages_as_read(user=request.user, conversation_id=conversation_id)
- render 'messaging/conversation.html' with MessageForm

---

### start_conversation_view
```python
@login_required
@require_http_methods(["POST"])
def start_conversation_view(request, listing_id):
```
- POST → call services.get_or_create_conversation(buyer=request.user, listing_id=listing_id)
  - PermissionError or ValueError → redirect back with error message
  - Success → redirect to 'messaging:conversation' with conversation.id

---

### send_message_view
```python
@login_required
@require_http_methods(["POST"])
def send_message_view(request, conversation_id):
```
- POST (AJAX) → validate MessageForm
  - Invalid → return JsonResponse({'errors': form.errors}, status=400)
  - Valid → call services.send_message(sender=request.user, conversation_id=conversation_id, body=...)
    - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
    - Success → return JsonResponse({
        'message_id': message.id,
        'body': message.body,
        'sender': message.sender.email,
        'created_at': message.created_at.isoformat(),
      })

---

### delete_message_view
```python
@login_required
@require_http_methods(["POST"])
def delete_message_view(request, message_id):
```
- POST (AJAX) → call services.delete_message(user=request.user, message_id=message_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Mesaj silindi.'})

---

### close_conversation_view
```python
@login_required
@require_http_methods(["POST"])
def close_conversation_view(request, conversation_id):
```
- POST → call services.close_conversation(user=request.user, conversation_id=conversation_id)
  - PermissionError → redirect back with error message
  - Success → redirect to 'messaging:inbox' with success message

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- messaging_models.md
- messaging_services.md
- selectors.md
- messaging/forms.py (already implemented)

### Task
Implement messaging/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. send_message_view and delete_message_view return JsonResponse (AJAX).
3. All other POST views follow PRG pattern.
4. mark_messages_as_read called automatically on conversation_view GET.
5. On PermissionError or ValueError → catch and handle gracefully.
6. Do NOT add extra views. Do NOT modify function signatures.

### Output
Single code block. messaging/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test messaging.tests.test_views
```
Manually verify in browser:
- GET /messaging/ renders inbox
- GET /messaging/<id>/ renders conversation and marks messages as read
- POST /messaging/start/<listing_id>/ creates or returns conversation
- POST /messaging/send/<id>/ returns JsonResponse with message data
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
