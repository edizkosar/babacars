# accounts/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.

## Purpose
Custom User model and SellerProfile model.
Extends Django's AbstractUser.

## Dependencies
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
```

## Models

---

### User
Extends AbstractUser. Adds role and contact fields.

| Field | Type | Options |
|-------|------|---------|
| `email` | EmailField | unique=True |
| `phone` | CharField | max_length=20, blank=True |
| `role` | CharField | choices=ROLE_CHOICES, max_length=10, default='buyer' |
| `avatar` | ImageField | upload_to='avatars/', blank=True, null=True |
| `email_verified` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**ROLE_CHOICES**
```python
ROLE_CHOICES = [
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
    ('both', 'Both'),
]
```

**Meta**
```python
class Meta:
    db_table = 'users'
    verbose_name = 'User'
    verbose_name_plural = 'Users'
```

**Methods**
```python
def is_seller(self) -> bool:
    return self.role in ['seller', 'both']

def is_buyer(self) -> bool:
    return self.role in ['buyer', 'both']

def __str__(self) -> str:
    return self.email
```

---

### SellerProfile
One-to-one with User. Created automatically when user becomes a seller.

| Field | Type | Options |
|-------|------|---------|
| `user` | OneToOneField | User, on_delete=CASCADE, related_name='seller_profile' |
| `bio` | TextField | blank=True |
| `is_verified` | BooleanField | default=False |
| `id_verified` | BooleanField | default=False |
| `total_sales` | PositiveIntegerField | default=0 |
| `avg_response_time` | DurationField | null=True, blank=True |
| `rating` | DecimalField | max_digits=3, decimal_places=2, default=0.00 |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**Meta**
```python
class Meta:
    db_table = 'seller_profiles'
    verbose_name = 'Seller Profile'
    verbose_name_plural = 'Seller Profiles'
```

**Methods**
```python
def __str__(self) -> str:
    return f"SellerProfile({self.user.email})"
```

---

### Review
Buyer reviews a seller after a completed transaction.

| Field | Type | Options |
|-------|------|---------|
| `reviewer` | ForeignKey | User, on_delete=CASCADE, related_name='given_reviews' |
| `seller` | ForeignKey | SellerProfile, on_delete=CASCADE, related_name='reviews' |
| `rating` | PositiveSmallIntegerField | choices=1–5 |
| `comment` | TextField | blank=True |
| `created_at` | DateTimeField | auto_now_add=True |

**RATING_CHOICES**
```python
RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
```

**Meta**
```python
class Meta:
    db_table = 'reviews'
    unique_together = ('reviewer', 'seller')
    verbose_name = 'Review'
    verbose_name_plural = 'Reviews'
```

**Methods**
```python
def __str__(self) -> str:
    return f"Review({self.reviewer.email} → {self.seller.user.email})"
```

---

## settings.py requirement
```python
AUTH_USER_MODEL = 'accounts.User'
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations accounts --check
python manage.py test accounts
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
