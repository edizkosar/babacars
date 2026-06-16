# admin.md

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See all models MD files for model definitions.

## Purpose
Django admin panel registration for all models.
Provides search, filter, and display configuration.

---

## accounts/admin.py

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User, SellerProfile, Review

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'email_verified', 'is_active', 'created_at']
    list_filter = ['role', 'email_verified', 'is_active']
    search_fields = ['email', 'phone']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BabaCars', {'fields': ('role', 'phone', 'avatar', 'email_verified')}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'id_verified', 'total_sales', 'rating']
    list_filter = ['is_verified', 'id_verified']
    search_fields = ['user__email']
    actions = ['verify_sellers']

    @admin.action(description='Seçili satıcıları doğrula')
    def verify_sellers(self, request, queryset):
        queryset.update(is_verified=True)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'seller', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['reviewer__email', 'seller__user__email']
```

---

## listings/admin.py

```python
from django.contrib import admin
from listings.models import Listing, Vehicle, Photo, Favorite, ListingView

class VehicleInline(admin.StackedInline):
    model = Vehicle
    extra = 0

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'listing_type', 'status', 'price', 'city', 'created_at']
    list_filter = ['listing_type', 'status', 'city']
    search_fields = ['title', 'seller__email']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    inlines = [VehicleInline, PhotoInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    search_fields = ['user__email', 'listing__title']


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['listing__title', 'user__email']
```

---

## offers/admin.py

```python
from django.contrib import admin
from offers.models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'amount', 'status', 'expires_at', 'created_at']
    list_filter = ['status']
    search_fields = ['listing__title', 'buyer__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
```

---

## bookings/admin.py

```python
from django.contrib import admin
from bookings.models import Booking, UnavailableDate

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'renter', 'start_date', 'end_date', 'total_price', 'status']
    list_filter = ['status']
    search_fields = ['listing__title', 'renter__email']
    ordering = ['-created_at']


@admin.register(UnavailableDate)
class UnavailableDateAdmin(admin.ModelAdmin):
    list_display = ['listing', 'start_date', 'end_date', 'reason']
    list_filter = ['reason']
    search_fields = ['listing__title']
```

---

## messaging/admin.py

```python
from django.contrib import admin
from messaging.models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'body', 'is_read', 'created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'seller', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['listing__title', 'buyer__email', 'seller__email']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'is_read', 'is_deleted', 'created_at']
    list_filter = ['is_read', 'is_deleted']
    search_fields = ['sender__email']
```

---

## notifications/admin.py

```python
from django.contrib import admin
from notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['recipient__email', 'title']
    ordering = ['-created_at']
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser  # test manually
```
Manually verify in browser at /admin/:
- All models appear in admin panel
- Search and filter fields work
- SellerProfile verify action works
- Listing inline shows Vehicle and Photos
Expected: 0 errors.
Report any errors before proceeding to next file.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- All models MD files

### Task
Implement all admin.py files exactly as defined in this document.

### Files to Create
- accounts/admin.py
- listings/admin.py
- offers/admin.py
- bookings/admin.py
- messaging/admin.py
- notifications/admin.py

### Rules
1. Copy code blocks exactly as written above.
2. Do NOT add extra ModelAdmin classes.
3. Do NOT register models not listed above.
4. Run Healthcheck after all files are created.

### Output
One code block per file. No explanations.
