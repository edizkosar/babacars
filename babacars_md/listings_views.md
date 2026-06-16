# listings/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See listings_models.md for Listing, Vehicle, Photo, Favorite, ListingView models.
See listings_services.md for all business logic.
See selectors.md → listings/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
Calls services.py for all actions. Calls selectors.py for all reads.

## Dependencies
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from listings import services, selectors
from listings.forms import ListingForm, VehicleForm, PhotoForm, SearchForm
```

## Views

---

### index_view
```python
@require_http_methods(["GET"])
def index_view(request):
```
- GET → fetch active listings via selectors.get_active_listings()
- Paginate: 12 listings per page
- render 'listings/index.html' with listings and page_obj

---

### search_view
```python
@require_http_methods(["GET"])
def search_view(request):
```
- GET → build filters dict from request.GET params
- call selectors.search_listings(filters=filters)
- Paginate: 12 per page
- render 'listings/search.html' with results, SearchForm, page_obj

---

### listing_detail_view
```python
@require_http_methods(["GET"])
def listing_detail_view(request, slug):
```
- GET → fetch listing via selectors.get_listing_by_slug(slug=slug)
- call services.track_view(listing_id=listing.id, user=request.user, ip_address=request.META.get('REMOTE_ADDR'))
- fetch photos via selectors.get_photos_by_listing(listing=listing)
- check if favorited: selectors.get_favorite(user=request.user, listing=listing) if authenticated
- render 'listings/detail.html'

---

### create_listing_view
```python
@login_required
@require_http_methods(["GET", "POST"])
def create_listing_view(request):
```
- GET → render 'listings/create.html' with ListingForm and VehicleForm
- POST → validate ListingForm and VehicleForm
  - Invalid → re-render with errors
  - Valid → call services.create_listing()
    - ValueError (photos < 8) → re-render with error message
    - PermissionError (not seller) → redirect to 'accounts:become_seller'
    - Success → redirect to 'listings:detail' with listing.slug

---

### edit_listing_view
```python
@login_required
@require_http_methods(["GET", "POST"])
def edit_listing_view(request, slug):
```
- GET → fetch listing → render 'listings/edit.html' with pre-filled forms
- POST → validate forms
  - Invalid → re-render with errors
  - Valid → call services.update_listing()
    - PermissionError → redirect to 'listings:index' with error message
    - Success → redirect to 'listings:detail' with listing.slug

---

### delete_listing_view
```python
@login_required
@require_http_methods(["POST"])
def delete_listing_view(request, listing_id):
```
- POST → call services.delete_listing(user=request.user, listing_id=listing_id)
  - PermissionError or ValueError → redirect back with error message
  - Success → redirect to 'accounts:profile' with success message

---

### toggle_favorite_view
```python
@login_required
@require_http_methods(["POST"])
def toggle_favorite_view(request, listing_id):
```
- POST (AJAX) → call services.toggle_favorite(user=request.user, listing_id=listing_id)
  - ValueError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'is_favorited': bool, 'favorite_count': int})

---

### my_favorites_view
```python
@login_required
@require_http_methods(["GET"])
def my_favorites_view(request):
```
- GET → fetch favorites via selectors.get_favorites_by_user(user=request.user)
- render 'listings/favorites.html'

---

### compare_view
```python
@require_http_methods(["GET", "POST"])
def compare_view(request):
```
- GET → get listing IDs from session ('compare_ids')
  - fetch each listing via selectors.get_listing_by_id
  - render 'listings/compare.html' with listings (max 3)
- POST (AJAX) → add or remove listing_id from session['compare_ids']
  - max 3 listings → return JsonResponse({'error': 'Max 3 araç eklenebilir.'}, status=400) if exceeded
  - return JsonResponse({'compare_count': int, 'in_compare': bool})

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- listings_models.md
- listings_services.md
- selectors.md
- listings/forms.py (already implemented)

### Task
Implement listings/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. All actions through services.py. All reads through selectors.py.
3. toggle_favorite_view and compare_view return JsonResponse (AJAX).
4. All other POST views follow PRG pattern (redirect after success).
5. Paginator used in index_view and search_view — 12 per page.
6. Compare list stored in request.session['compare_ids'] as a list of ints.
7. On PermissionError or ValueError → catch and show user-friendly message.
8. Do NOT add extra views. Do NOT modify function signatures.

### Output
Single code block. listings/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test listings.tests.test_views
```
Manually verify in browser:
- GET /listings/ renders index with pagination
- GET /listings/search/ returns filtered results
- GET /listings/<slug>/ renders detail and increments view_count
- POST /listings/favorite/<id>/ returns JsonResponse
- POST /listings/compare/ updates session and returns JsonResponse
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
