# dashboard/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See dashboard_services.md for all analytics logic.
See selectors.md → dashboard/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
Seller-only views. All data comes from dashboard/services.py.

## Dependencies
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from dashboard import services
from listings import selectors as listing_selectors
```

## Views

---

### dashboard_view
```python
@login_required
@require_http_methods(["GET"])
def dashboard_view(request):
```
- GET → check request.user.is_seller()
  - False → redirect to 'accounts:become_seller' with info message
- call services.get_dashboard_summary(user=request.user)
- fetch listings via listing_selectors.get_listings_by_seller(seller=request.user)
- render 'dashboard/dashboard.html' with summary and listings

---

### listing_stats_view
```python
@login_required
@require_http_methods(["GET"])
def listing_stats_view(request, listing_id):
```
- GET → call services.get_listing_stats(user=request.user, listing_id=listing_id)
  - PermissionError → redirect to 'dashboard:dashboard' with error message
  - Success → render 'dashboard/listing_stats.html' with stats

---

### listing_traffic_view
```python
@login_required
@require_http_methods(["GET"])
def listing_traffic_view(request, listing_id):
```
- GET (AJAX) → call services.get_hourly_traffic and services.get_daily_traffic
  - PermissionError → return JsonResponse({'error': str(e)}, status=400)
  - Success → return JsonResponse({'hourly': list, 'daily': list})
- Used by dashboard charts (GSAP + chart rendering)

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- dashboard_services.md
- selectors.md

### Task
Implement dashboard/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. All data from dashboard/services.py only.
3. listing_traffic_view returns JsonResponse (AJAX) for chart data.
4. Non-sellers redirected to become_seller on dashboard_view.
5. On PermissionError → catch and handle gracefully.
6. Do NOT add extra views. Do NOT modify function signatures.

### Output
Single code block. dashboard/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test dashboard.tests.test_views
```
Manually verify in browser:
- GET /dashboard/ redirects non-sellers to become_seller
- GET /dashboard/ renders summary for sellers
- GET /dashboard/listing/<id>/ renders stats for listing owner only
- GET /dashboard/listing/<id>/traffic/ returns JsonResponse with hourly and daily data
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
