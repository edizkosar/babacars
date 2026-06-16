# accounts/services.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User, SellerProfile, Review models.

## Purpose
All business logic for user registration, profile management, seller profile and reviews.
No HTTP logic. No ORM queries. Calls selectors.py for data access.

## Dependencies
```python
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import SellerProfile, Review
from accounts import selectors

User = get_user_model()
```

## Functions

---

### register_user
```python
def register_user(*, email: str, password: str, phone: str = '', role: str = 'buyer') -> User:
```
- Validates email is not already taken (calls selectors.get_user_by_email)
- Raises ValueError if email exists
- Creates User via User.objects.create_user()
- Sets user.email_verified=False
- Sends verification email via send_verification_email()
- Does not create SellerProfile here

---

### send_verification_email
```python
def send_verification_email(*, user: User) -> None:
```
- Generates a signed verification token via Django's signing module
- Sends email to user.email with verification link
- Link format: /accounts/verify-email/?token=<signed_token>

---

### verify_email
```python
def verify_email(*, token: str) -> User:
```
- Decodes and validates token via Django's signing module
- Raises ValueError if token is invalid or expired (max_age=86400 → 24 hours)
- Sets user.email_verified=True
- Returns verified User

---

### update_user_profile
```python
def update_user_profile(*, user: User, email: str = None, phone: str = None, avatar=None) -> User:
```
- Updates only provided fields
- Validates email uniqueness if email is being changed
- Saves and returns updated user

---

### become_seller
```python
def become_seller(*, user: User) -> SellerProfile:
```
- Raises ValueError if user.phone is empty
- Raises ValueError if user.email is not verified (checks user.email_verified)
- Updates user.role to 'seller' if role is 'buyer', else 'both'
- Creates SellerProfile if not already exists
- Sets SellerProfile.is_verified=False by default (admin verifies manually)
- Returns SellerProfile

---

### update_seller_profile
```python
def update_seller_profile(*, user: User, bio: str = None) -> SellerProfile:
```
- Updates SellerProfile.bio if provided
- Raises ValueError if user has no SellerProfile
- Returns updated SellerProfile

---

### create_review
```python
def create_review(*, reviewer: User, seller_profile: SellerProfile, rating: int, comment: str = '') -> Review:
```
- Raises ValueError if reviewer == seller_profile.user
- Raises ValueError if review already exists (calls selectors.get_review)
- Validates rating is between 1 and 5
- Creates Review
- Updates seller_profile.rating as average of all reviews
- Returns created Review

---

### delete_review
```python
def delete_review(*, reviewer: User, review_id: int) -> None:
```
- Fetches review via selectors.get_review_by_id
- Raises PermissionError if reviewer != review.reviewer
- Deletes review
- Recalculates and updates seller_profile.rating

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test accounts.tests.test_services
```
Manually verify:
- register_user creates user with email_verified=False
- verify_email sets email_verified=True
- become_seller raises ValueError if phone is empty
- become_seller raises ValueError if email_verified is False
- create_review raises ValueError if reviewer == seller
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
