# urls.md

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See all views MD files for view function names.

## Purpose
URL routing only. One urls.py per app + main project urls.py.

## Rules
- All URL names in kebab-case
- All app namespaces defined
- No logic in urls.py files

---

## babacars/urls.py (main project)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls', namespace='listings')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('offers/', include('offers.urls', namespace='offers')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('api/v1/', include('api.urls', namespace='api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## accounts/urls.py

```python
from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('verify-email/notice/', views.verify_email_notice_view, name='verify_email_notice'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('become-seller/', views.become_seller_view, name='become_seller'),
    path('seller/<int:seller_id>/', views.seller_profile_view, name='seller_profile'),
    path('seller/<int:seller_id>/review/', views.create_review_view, name='create_review'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
]
```

---

## listings/urls.py

```python
from django.urls import path
from listings import views

app_name = 'listings'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('search/', views.search_view, name='search'),
    path('create/', views.create_listing_view, name='create'),
    path('compare/', views.compare_view, name='compare'),
    path('favorites/', views.my_favorites_view, name='favorites'),
    path('<slug:slug>/', views.listing_detail_view, name='detail'),
    path('<slug:slug>/edit/', views.edit_listing_view, name='edit'),
    path('<int:listing_id>/delete/', views.delete_listing_view, name='delete'),
    path('<int:listing_id>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
]
```

---

## offers/urls.py

```python
from django.urls import path
from offers import views

app_name = 'offers'

urlpatterns = [
    path('create/<int:listing_id>/', views.create_offer_view, name='create'),
    path('<int:offer_id>/accept/', views.accept_offer_view, name='accept'),
    path('<int:offer_id>/reject/', views.reject_offer_view, name='reject'),
    path('<int:offer_id>/counter/', views.counter_offer_view, name='counter'),
    path('<int:offer_id>/cancel/', views.cancel_offer_view, name='cancel'),
    path('my-offers/', views.my_offers_view, name='my_offers'),
    path('listing/<int:listing_id>/', views.listing_offers_view, name='listing_offers'),
]
```

---

## bookings/urls.py

```python
from django.urls import path
from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('<int:booking_id>/', views.booking_detail_view, name='detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel'),
    path('block/<int:listing_id>/', views.block_dates_view, name='block_dates'),
    path('unblock/<int:unavailable_date_id>/', views.unblock_dates_view, name='unblock_dates'),
    path('availability/<int:listing_id>/', views.check_availability_view, name='check_availability'),
]
```

---

## messaging/urls.py

```python
from django.urls import path
from messaging import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('start/<int:listing_id>/', views.start_conversation_view, name='start'),
    path('<int:conversation_id>/send/', views.send_message_view, name='send'),
    path('message/<int:message_id>/delete/', views.delete_message_view, name='delete_message'),
    path('<int:conversation_id>/close/', views.close_conversation_view, name='close'),
]
```

---

## notifications/urls.py

```python
from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='list'),
    path('<int:notification_id>/read/', views.mark_as_read_view, name='mark_as_read'),
    path('read-all/', views.mark_all_as_read_view, name='mark_all_as_read'),
    path('unread-count/', views.unread_count_view, name='unread_count'),
]
```

---

## dashboard/urls.py

```python
from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('listing/<int:listing_id>/', views.listing_stats_view, name='listing_stats'),
    path('listing/<int:listing_id>/traffic/', views.listing_traffic_view, name='listing_traffic'),
]
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py show_urls  # if django-extensions installed, optional
```
Manually verify:
- All app namespaces match views imports
- No duplicate URL names within same namespace
- Main urls.py includes all app urls
- MEDIA_URL served correctly in development
Expected: 0 errors.
Report any errors before proceeding to next file.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- All views MD files

### Task
Implement all urls.py files exactly as defined in this document.

### Files to Create
- babacars/urls.py
- accounts/urls.py
- listings/urls.py
- offers/urls.py
- bookings/urls.py
- messaging/urls.py
- notifications/urls.py
- dashboard/urls.py

### Rules
1. URL routing only. No logic.
2. Every app urls.py defines app_name for namespace.
3. Copy code blocks exactly as written above.
4. Do NOT add extra URL patterns.
5. Run Healthcheck after implementation.

### Output
One code block per file. No explanations.
