# listings/models.py

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See accounts_models.md for User model.

## Purpose
Vehicle listing, photo, favorite and view tracking models.

## Dependencies
```python
from django.db import models
from django.conf import settings
from django.utils.text import slugify
```

## Models

---

### Listing
Core listing model. Supports both sale and rental types.

| Field | Type | Options |
|-------|------|---------|
| `seller` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='listings' |
| `listing_type` | CharField | choices=LISTING_TYPE_CHOICES, max_length=10 |
| `status` | CharField | choices=STATUS_CHOICES, max_length=10, default='active' |
| `title` | CharField | max_length=255 |
| `slug` | SlugField | unique=True, blank=True |
| `description` | TextField | |
| `price` | DecimalField | max_digits=12, decimal_places=2 |
| `currency` | CharField | max_length=3, default='TRY' |
| `city` | CharField | max_length=100 |
| `district` | CharField | max_length=100, blank=True |
| `latitude` | DecimalField | max_digits=9, decimal_places=6, null=True, blank=True |
| `longitude` | DecimalField | max_digits=9, decimal_places=6, null=True, blank=True |
| `view_count` | PositiveIntegerField | default=0 |
| `favorite_count` | PositiveIntegerField | default=0 |
| `is_featured` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**LISTING_TYPE_CHOICES**
```python
LISTING_TYPE_CHOICES = [
    ('sale', 'For Sale'),
    ('rental', 'For Rent'),
]
```

**STATUS_CHOICES**
```python
STATUS_CHOICES = [
    ('active', 'Active'),
    ('sold', 'Sold'),
    ('rented', 'Rented'),
    ('passive', 'Passive'),
    ('pending', 'Pending Review'),
]
```

**Meta**
```python
class Meta:
    db_table = 'listings'
    ordering = ['-created_at']
    verbose_name = 'Listing'
    verbose_name_plural = 'Listings'
```

**Methods**
```python
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.title)
    super().save(*args, **kwargs)

def __str__(self) -> str:
    return f"{self.title} ({self.listing_type})"
```

---

### Vehicle
Specs model. One-to-one with Listing.

| Field | Type | Options |
|-------|------|---------|
| `listing` | OneToOneField | Listing, on_delete=CASCADE, related_name='vehicle' |
| `make` | CharField | max_length=100 (e.g. BMW) |
| `model` | CharField | max_length=100 (e.g. 320i) |
| `year` | PositiveSmallIntegerField | |
| `mileage` | PositiveIntegerField | help_text='km' |
| `fuel_type` | CharField | choices=FUEL_CHOICES, max_length=20 |
| `transmission` | CharField | choices=TRANSMISSION_CHOICES, max_length=20 |
| `body_type` | CharField | choices=BODY_CHOICES, max_length=20 |
| `color` | CharField | max_length=50 |
| `engine_cc` | PositiveSmallIntegerField | null=True, blank=True, help_text='cc' |
| `horsepower` | PositiveSmallIntegerField | null=True, blank=True, help_text='hp' |
| `torque` | PositiveSmallIntegerField | null=True, blank=True, help_text='Nm' |
| `trunk_volume` | PositiveSmallIntegerField | null=True, blank=True, help_text='liters' |
| `fuel_consumption` | DecimalField | max_digits=4, decimal_places=1, null=True, blank=True, help_text='L/100km' |
| `num_doors` | PositiveSmallIntegerField | default=4 |
| `num_seats` | PositiveSmallIntegerField | default=5 |

**FUEL_CHOICES**
```python
FUEL_CHOICES = [
    ('gasoline', 'Gasoline'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
    ('hybrid', 'Hybrid'),
    ('lpg', 'LPG'),
]
```

**TRANSMISSION_CHOICES**
```python
TRANSMISSION_CHOICES = [
    ('manual', 'Manual'),
    ('automatic', 'Automatic'),
    ('semi_auto', 'Semi-Automatic'),
]
```

**BODY_CHOICES**
```python
BODY_CHOICES = [
    ('sedan', 'Sedan'),
    ('hatchback', 'Hatchback'),
    ('suv', 'SUV'),
    ('coupe', 'Coupe'),
    ('convertible', 'Convertible'),
    ('wagon', 'Wagon'),
    ('van', 'Van'),
    ('pickup', 'Pickup'),
]
```

**Meta**
```python
class Meta:
    db_table = 'vehicles'
    verbose_name = 'Vehicle'
    verbose_name_plural = 'Vehicles'
```

**Methods**
```python
def __str__(self) -> str:
    return f"{self.make} {self.model} {self.year}"
```

---

### Photo
Vehicle photos. Minimum 8 photos enforced at form level.

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='photos' |
| `image` | ImageField | upload_to='listings/photos/' |
| `is_cover` | BooleanField | default=False |
| `order` | PositiveSmallIntegerField | default=0 |
| `created_at` | DateTimeField | auto_now_add=True |

**Meta**
```python
class Meta:
    db_table = 'photos'
    ordering = ['order']
    verbose_name = 'Photo'
    verbose_name_plural = 'Photos'
```

**Methods**
```python
def __str__(self) -> str:
    return f"Photo({self.listing.title} – #{self.order})"
```

---

### Favorite
User favorites a listing.

| Field | Type | Options |
|-------|------|---------|
| `user` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='favorites' |
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='favorited_by' |
| `created_at` | DateTimeField | auto_now_add=True |

**Meta**
```python
class Meta:
    db_table = 'favorites'
    unique_together = ('user', 'listing')
    verbose_name = 'Favorite'
    verbose_name_plural = 'Favorites'
```

**Methods**
```python
def __str__(self) -> str:
    return f"Favorite({self.user.email} → {self.listing.title})"
```

---

### ListingView
Tracks listing view events for dashboard analytics.

| Field | Type | Options |
|-------|------|---------|
| `listing` | ForeignKey | Listing, on_delete=CASCADE, related_name='views' |
| `user` | ForeignKey | settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True |
| `ip_address` | GenericIPAddressField | null=True, blank=True |
| `viewed_at` | DateTimeField | auto_now_add=True |

**Meta**
```python
class Meta:
    db_table = 'listing_views'
    verbose_name = 'Listing View'
    verbose_name_plural = 'Listing Views'
```

**Methods**
```python
def __str__(self) -> str:
    return f"View({self.listing.title} at {self.viewed_at})"
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations listings --check
python manage.py test listings
```
Expected: 0 errors, 0 failures, 0 warnings.
Report any errors before proceeding to next file.
