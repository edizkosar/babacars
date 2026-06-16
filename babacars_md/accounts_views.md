# accounts/views.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User, SellerProfile, Review models.
See accounts_services.md for all business logic.
See selectors.md → accounts/selectors.py for all queries.

## Purpose
HTTP layer only. No business logic. No ORM queries.
Calls services.py for all actions. Calls selectors.py for all reads.
Handles request/response, redirects, and template rendering.

## Dependencies
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from accounts import services, selectors
from accounts.forms import RegisterForm, LoginForm, ProfileUpdateForm, BecomeSellerForm
```

## Views

---

### register_view
```python
@require_http_methods(["GET", "POST"])
def register_view(request):
```
- GET → render 'accounts/register.html' with RegisterForm
- POST → validate RegisterForm
  - Invalid → re-render form with errors
  - Valid → call services.register_user() with form data
    - ValueError (email exists) → re-render form with error message
    - Success → redirect to 'accounts:verify_email_notice'

---

### verify_email_notice_view
```python
@require_http_methods(["GET"])
def verify_email_notice_view(request):
```
- GET → render 'accounts/verify_email_notice.html'

---

### verify_email_view
```python
@require_http_methods(["GET"])
def verify_email_view(request):
```
- GET → get token from request.GET
  - call services.verify_email(token=token)
    - ValueError (invalid/expired) → render 'accounts/verify_email_failed.html'
    - Success → redirect to 'accounts:login' with success message

---

### login_view
```python
@require_http_methods(["GET", "POST"])
def login_view(request):
```
- GET → render 'accounts/login.html' with LoginForm
- POST → validate LoginForm
  - Invalid → re-render form with errors
  - Valid → authenticate user
    - Fail → re-render form with 'Geçersiz e-posta veya şifre.' error
    - Success → login(request, user) → redirect to 'listings:index'

---

### logout_view
```python
@login_required
@require_http_methods(["POST"])
def logout_view(request):
```
- POST → logout(request) → redirect to 'listings:index'

---

### profile_view
```python
@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
```
- GET → fetch seller_profile if exists → render 'accounts/profile.html'
- POST → validate ProfileUpdateForm
  - Invalid → re-render with errors
  - Valid → call services.update_user_profile()
    - Success → redirect to 'accounts:profile' with success message

---

### become_seller_view
```python
@login_required
@require_http_methods(["GET", "POST"])
def become_seller_view(request):
```
- GET → render 'accounts/become_seller.html' with BecomeSellerForm
- POST → validate BecomeSellerForm
  - Invalid → re-render with errors
  - Valid → call services.become_seller(user=request.user)
    - ValueError (missing phone or unverified email) → re-render with error message
    - Success → redirect to 'accounts:profile' with success message

---

### seller_profile_view
```python
@require_http_methods(["GET"])
def seller_profile_view(request, seller_id):
```
- GET → fetch SellerProfile via selectors.get_seller_profile_by_id
  - fetch reviews via selectors.get_reviews_by_seller
  - fetch listings via listings.selectors.get_listings_by_seller
  - render 'accounts/seller_profile.html'

---

### create_review_view
```python
@login_required
@require_http_methods(["POST"])
def create_review_view(request, seller_id):
```
- POST → call services.create_review()
  - ValueError → redirect back with error message
  - Success → redirect to 'accounts:seller_profile' with success message

---

### delete_review_view
```python
@login_required
@require_http_methods(["POST"])
def delete_review_view(request, review_id):
```
- POST → call services.delete_review(reviewer=request.user, review_id=review_id)
  - PermissionError → redirect back with error message
  - Success → redirect back with success message

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- accounts_models.md
- accounts_services.md
- selectors.md
- accounts/forms.py (already implemented)

### Task
Implement accounts/views.py exactly as defined above.

### Rules
1. HTTP logic only. No ORM queries. No business logic.
2. All actions go through services.py. All reads go through selectors.py.
3. Use @login_required on all views that require authentication.
4. Use @require_http_methods on every view.
5. On ValueError or PermissionError → never raise — catch and show user-friendly message via django.contrib.messages.
6. On success → always redirect, never re-render (PRG pattern).
7. Do NOT add extra views.
8. Do NOT modify function signatures.

### Output
Single code block. accounts/views.py only. No explanations.

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test accounts.tests.test_views
```
Manually verify in browser:
- GET /accounts/register/ renders form
- POST /accounts/register/ with valid data redirects to verify_email_notice
- GET /accounts/login/ renders form
- POST /accounts/login/ with valid credentials redirects to listings:index
- POST /accounts/logout/ redirects to listings:index
- GET /accounts/profile/ requires login
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
