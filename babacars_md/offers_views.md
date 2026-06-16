# offers/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See offers_models.md for Offer model.
See offers_services.md for all business logic.
See selectors.md → offers/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
All offer actions are AJAX (JsonResponse) except list views.

## Dependencies
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from offers import services, selectors
from offers.forms import OfferForm, CounterOfferForm
```

## Views

---

### create_offer_view
```python
@login_required
@require_http_methods(["POST"])
def create_offer_view(request, listing_id):
```
- POST (AJAX) → validate OfferForm
  - Invalid → return JsonResponse({'errors': form.errors}, status=400)
  - Valid → call services.create_offer(buyer=request.user, listing_id=listing_id, ...)
    - ValueError or PermissionError → return JsonResponse({'error': str(e)}, status=400)
    - Success → return JsonResponse({'message': 'Teklifiniz gönderildi.', 'offer_id': offer.id})

---

### accept_offer_view
```python
@login_required
@require_http_methods(["POST"])
def accept_offer_view(request, offer_id):
```
- POST (AJAX) → call services.accept_offer(user=request.user, offer_id=offer_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Teklif kabul edildi.'})

---

### reject_offer_view
```python
@login_required
@require_http_methods(["POST"])
def reject_offer_view(request, offer_id):
```
- POST (AJAX) → call services.reject_offer(user=request.user, offer_id=offer_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Teklif reddedildi.'})

---

### counter_offer_view
```python
@login_required
@require_http_methods(["POST"])
def counter_offer_view(request, offer_id):
```
- POST (AJAX) → validate CounterOfferForm
  - Invalid → return JsonResponse({'errors': form.errors}, status=400)
  - Valid → call services.counter_offer(user=request.user, offer_id=offer_id, ...)
    - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
    - Success → return JsonResponse({'message': 'Karşı teklifiniz gönderildi.', 'offer_id': new_offer.id})

---

### cancel_offer_view
```python
@login_required
@require_http_methods(["POST"])
def cancel_offer_view(request, offer_id):
```
- POST (AJAX) → call services.cancel_offer(user=request.user, offer_id=offer_id)
  - PermissionError or ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'message': 'Teklif iptal edildi.'})

---

### my_offers_view
```python
@login_required
@require_http_methods(["GET"])
def my_offers_view(request):
```
- GET → fetch sent offers via selectors.get_offers_by_buyer(buyer=request.user)
- render 'offers/my_offers.html'

---

### listing_offers_view
```python
@login_required
@require_http_methods(["GET"])
def listing_offers_view(request, listing_id):
```
- GET → fetch listing offers via selectors.get_offers_by_listing
- Raises PermissionError if request.user != listing.seller → redirect with error
- render 'offers/listing_offers.html'

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- offers_models.md
- offers_services.md
- selectors.md
- offers/forms.py (already implemented)

### Task
Implement offers/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. All offer action views (create, accept, reject, counter, cancel) return JsonResponse — AJAX only.
3. List views (my_offers, listing_offers) return rendered templates.
4. On PermissionError or ValueError → catch and return JsonResponse with error key and status=400.
5. Do NOT add extra views. Do NOT modify function signatures.
6. Do NOT use @csrf_exempt — CSRF handled via JS headers.

### Output
Single code block. offers/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test offers.tests.test_views
```
Manually verify in browser:
- POST /offers/create/<listing_id>/ returns JsonResponse
- POST /offers/accept/<offer_id>/ returns JsonResponse
- POST /offers/reject/<offer_id>/ returns JsonResponse
- POST /offers/counter/<offer_id>/ returns JsonResponse
- GET /offers/my-offers/ renders template
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
