# bookings/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See bookings_models.md for Booking, UnavailableDate models.
See bookings_services.md for all business logic.
See selectors.md → bookings/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
Booking creation is triggered from offers/views.py — not directly from here.

## Dependencies
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from bookings import services, selectors
```

## Views

---

### my_bookings_view
```python
@login_required
@require_http_methods(["GET"])
def my_bookings_view(request):
```
- GET → fetch bookings via selectors.get_bookings_by_renter(renter=request.user)
- render 'bookings/my_bookings.html'

---

### booking_detail_view
```python
@login_required
@require_http_methods(["GET"])
def booking_detail_view(request, booking_id):
```
- GET → fetch booking via selectors.get_booking_by_id(booking_id=booking_id)
  - Raises PermissionError if request.user not in [booking.renter, booking.listing.seller]
  - → redirect to 'listings:index' with error message
- render 'bookings/booking_detail.html'

---

### cancel_booking_view
```python
@login_required
@require_http_methods(["POST"])
def cancel_booking_view(request, booking_id):
```
- POST → call services.cancel_booking(user=request.user, booking_id=booking_id)
  - PermissionError or ValueError → redirect back with error message
  - Success → redirect to 'bookings:my_bookings' with success message

---

### block_dates_view
```python
@login_required
@require_http_methods(["POST"])
def block_dates_view(request, listing_id):
```
- POST (AJAX) → call services.block_dates(user=request.user, listing_id=listing_id, ...)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Tarihler bloklandı.'})

---

### unblock_dates_view
```python
@login_required
@require_http_methods(["POST"])
def unblock_dates_view(request, unavailable_date_id):
```
- POST (AJAX) → call services.unblock_dates(user=request.user, unavailable_date_id=unavailable_date_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Blok kaldırıldı.'})

---

### check_availability_view
```python
@require_http_methods(["GET"])
def check_availability_view(request, listing_id):
```
- GET (AJAX) → get start_date and end_date from request.GET
  - call services.check_availability(listing_id=listing_id, start_date=..., end_date=...)
  - return JsonResponse({'available': bool})

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- bookings_models.md
- bookings_services.md
- selectors.md

### Task
Implement bookings/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. block_dates, unblock_dates, check_availability return JsonResponse (AJAX).
3. cancel_booking follows PRG pattern (redirect after POST).
4. Booking creation is NOT handled here — it is triggered from offers/services.py.
5. On PermissionError or ValueError → catch and handle gracefully.
6. Do NOT add extra views. Do NOT modify function signatures.

### Output
Single code block. bookings/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test bookings.tests.test_views
```
Manually verify in browser:
- GET /bookings/my-bookings/ renders template
- GET /bookings/<id>/ shows booking detail for owner only
- POST /bookings/cancel/<id>/ redirects to my_bookings
- GET /bookings/availability/<listing_id>/ returns JsonResponse with available bool
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
