# notifications/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See notifications_models.md for Notification model.
See notifications_services.md for all business logic.
See selectors.md → notifications/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
All notification actions are AJAX except the list view.

## Dependencies
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from notifications import services, selectors
```

## Views

---

### notifications_view
```python
@login_required
@require_http_methods(["GET"])
def notifications_view(request):
```
- GET → fetch notifications via selectors.get_notifications_by_user(user=request.user)
- render 'notifications/notifications.html'

---

### mark_as_read_view
```python
@login_required
@require_http_methods(["POST"])
def mark_as_read_view(request, notification_id):
```
- POST (AJAX) → call services.mark_as_read(user=request.user, notification_id=notification_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Bildirim okundu olarak işaretlendi.'})

---

### mark_all_as_read_view
```python
@login_required
@require_http_methods(["POST"])
def mark_all_as_read_view(request):
```
- POST (AJAX) → call services.mark_all_as_read(user=request.user)
  - Success → return JsonResponse({'message': 'Tüm bildirimler okundu.', 'count': int})

---

### unread_count_view
```python
@login_required
@require_http_methods(["GET"])
def unread_count_view(request):
```
- GET (AJAX) → call services.get_unread_count(user=request.user)
- return JsonResponse({'unread_count': int})
- Used by navbar to poll unread badge every 30 seconds

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- notifications_models.md
- notifications_services.md
- selectors.md

### Task
Implement notifications/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. mark_as_read, mark_all_as_read, unread_count return JsonResponse (AJAX).
3. notifications_view returns rendered template.
4. On PermissionError or ValueError → catch and return JsonResponse with error and status=400.
5. Do NOT add extra views. Do NOT modify function signatures.

### Output
Single code block. notifications/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test notifications.tests.test_views
```
Manually verify in browser:
- GET /notifications/ renders list
- POST /notifications/read/<id>/ returns JsonResponse
- POST /notifications/read-all/ returns JsonResponse with count
- GET /notifications/unread-count/ returns JsonResponse with unread_count
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
