# new_features_backend.md

## Reference
See PROJECT_OVERVIEW.md, AI_CONSTRAINTS.md.
See listings_models.md, notifications_models.md, notifications_services.md.

## Purpose
Backend features requiring new models, services, selectors, views, urls.
Token-efficient: grouped into one file, minimal boilerplate.

## Features in this file
1. Price Alert (Fiyat Alarmı)
2. Saved Search (Kayıtlı Arama)
3. Price Watch / Watchlist (İzleme Listesi)
4. Listing Report (İlan Rapor)
5. Vehicle Valuation (Araç Değerleme)
6. Listing Refresh (İlan Yenileme)
7. Bulk Listing Management (Toplu İlan Yönetimi)
8. Damage Report (Araç Hasar Raporu)

---

## 1. New App: alerts

Create new app `alerts` for price alerts, saved searches, watchlist.
Add to INSTALLED_APPS in settings.py: `'alerts',`

### alerts/models.py
```python
from django.db import models
from django.conf import settings


class PriceAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_alerts')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='price_alerts')
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'price_alerts'
        unique_together = ('user', 'listing')
        verbose_name = 'Price Alert'
        verbose_name_plural = 'Price Alerts'

    def __str__(self) -> str:
        return f"PriceAlert({self.user.email} → {self.listing.title} @ {self.target_price})"


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters_json = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_searches'
        ordering = ['-created_at']
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'

    def __str__(self) -> str:
        return f"SavedSearch({self.user.email} | {self.name})"


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='watched_by')
    last_known_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'listing')
        verbose_name = 'Watchlist Item'
        verbose_name_plural = 'Watchlist Items'

    def __str__(self) -> str:
        return f"Watchlist({self.user.email} → {self.listing.title})"
```

### alerts/selectors.py
```python
from django.db.models import QuerySet
from alerts.models import PriceAlert, SavedSearch, Watchlist


def get_active_price_alerts() -> QuerySet:
    return PriceAlert.objects.filter(is_active=True, triggered=False).select_related('listing', 'user')


def get_user_price_alerts(*, user) -> QuerySet:
    return PriceAlert.objects.filter(user=user).select_related('listing')


def get_price_alert(*, user, listing) -> PriceAlert:
    return PriceAlert.objects.get(user=user, listing=listing)


def get_user_saved_searches(*, user) -> QuerySet:
    return SavedSearch.objects.filter(user=user)


def get_active_saved_searches() -> QuerySet:
    return SavedSearch.objects.filter(is_active=True).select_related('user')


def get_saved_search_by_id(*, search_id: int) -> SavedSearch:
    return SavedSearch.objects.get(id=search_id)


def get_user_watchlist(*, user) -> QuerySet:
    return Watchlist.objects.filter(user=user).select_related('listing__vehicle').prefetch_related('listing__photos')


def get_active_watchlist() -> QuerySet:
    return Watchlist.objects.select_related('listing', 'user')


def get_watchlist_item(*, user, listing) -> Watchlist:
    return Watchlist.objects.get(user=user, listing=listing)
```

### alerts/services.py
```python
from alerts.models import PriceAlert, SavedSearch, Watchlist
from alerts import selectors
from notifications.services import create_notification


def create_price_alert(*, user, listing_id: int, target_price: float) -> PriceAlert:
    from listings.selectors import get_listing_by_id
    listing = get_listing_by_id(listing_id=listing_id)
    if target_price <= 0:
        raise ValueError('Hedef fiyat sıfırdan büyük olmalıdır.')
    alert, created = PriceAlert.objects.get_or_create(
        user=user, listing=listing,
        defaults={'target_price': target_price}
    )
    if not created:
        alert.target_price = target_price
        alert.triggered = False
        alert.is_active = True
        alert.save()
    return alert


def delete_price_alert(*, user, alert_id: int) -> None:
    alert = PriceAlert.objects.get(id=alert_id)
    if alert.user != user:
        raise PermissionError('Bu alarmı silme yetkiniz yok.')
    alert.delete()


def check_price_alerts() -> int:
    # Called from middleware. Checks if any listing price dropped to/below target.
    count = 0
    for alert in selectors.get_active_price_alerts():
        if alert.listing.price <= alert.target_price and alert.listing.status == 'active':
            create_notification(
                recipient=alert.user,
                notification_type='new_message',
                title='Fiyat Alarmı',
                body=f'{alert.listing.title} ilanı {alert.listing.price} TL oldu (hedef: {alert.target_price} TL).',
                related_object=alert.listing,
            )
            alert.triggered = True
            alert.save(update_fields=['triggered'])
            count += 1
    return count


def create_saved_search(*, user, name: str, filters: dict) -> SavedSearch:
    if not name.strip():
        raise ValueError('Arama adı boş olamaz.')
    return SavedSearch.objects.create(user=user, name=name, filters_json=filters)


def delete_saved_search(*, user, search_id: int) -> None:
    search = selectors.get_saved_search_by_id(search_id=search_id)
    if search.user != user:
        raise PermissionError('Bu aramayı silme yetkiniz yok.')
    search.delete()


def check_saved_searches() -> int:
    # Called from middleware. Notifies users when new listings match their saved searches.
    from django.utils import timezone
    from listings.selectors import search_listings
    count = 0
    for search in selectors.get_active_saved_searches():
        results = search_listings(filters=search.filters_json)
        if search.last_checked_at:
            new_results = results.filter(created_at__gt=search.last_checked_at)
        else:
            new_results = results.none()
        new_count = new_results.count()
        if new_count > 0:
            create_notification(
                recipient=search.user,
                notification_type='new_message',
                title='Kayıtlı Arama',
                body=f'"{search.name}" aramanıza uygun {new_count} yeni ilan var.',
            )
            count += new_count
        search.last_checked_at = timezone.now()
        search.save(update_fields=['last_checked_at'])
    return count


def add_to_watchlist(*, user, listing_id: int) -> Watchlist:
    from listings.selectors import get_listing_by_id
    listing = get_listing_by_id(listing_id=listing_id)
    if user == listing.seller:
        raise PermissionError('Kendi ilanınızı izleyemezsiniz.')
    item, created = Watchlist.objects.get_or_create(
        user=user, listing=listing,
        defaults={'last_known_price': listing.price}
    )
    return item


def remove_from_watchlist(*, user, listing_id: int) -> None:
    from listings.selectors import get_listing_by_id
    listing = get_listing_by_id(listing_id=listing_id)
    Watchlist.objects.filter(user=user, listing=listing).delete()


def check_watchlist_price_changes() -> int:
    # Called from middleware. Notifies users when a watched listing price changes.
    count = 0
    for item in selectors.get_active_watchlist():
        if item.listing.price != item.last_known_price:
            direction = 'düştü' if item.listing.price < item.last_known_price else 'arttı'
            create_notification(
                recipient=item.user,
                notification_type='new_message',
                title='Fiyat Değişikliği',
                body=f'{item.listing.title} fiyatı {direction}: {item.last_known_price} → {item.listing.price} TL.',
                related_object=item.listing,
            )
            item.last_known_price = item.listing.price
            item.save(update_fields=['last_known_price'])
            count += 1
    return count
```

### alerts/views.py
```python
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from alerts import services, selectors


@login_required
@require_http_methods(["POST"])
def create_price_alert_view(request, listing_id):
    try:
        data = json.loads(request.body)
        alert = services.create_price_alert(
            user=request.user, listing_id=listing_id,
            target_price=float(data.get('target_price'))
        )
        return JsonResponse({'message': 'Fiyat alarmı kuruldu.', 'alert_id': alert.id})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_price_alert_view(request, alert_id):
    try:
        services.delete_price_alert(user=request.user, alert_id=alert_id)
        return JsonResponse({'message': 'Alarm silindi.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def save_search_view(request):
    try:
        data = json.loads(request.body)
        search = services.create_saved_search(
            user=request.user, name=data.get('name', ''),
            filters=data.get('filters', {})
        )
        return JsonResponse({'message': 'Arama kaydedildi.', 'search_id': search.id})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_saved_search_view(request, search_id):
    try:
        services.delete_saved_search(user=request.user, search_id=search_id)
        return JsonResponse({'message': 'Arama silindi.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def toggle_watchlist_view(request, listing_id):
    try:
        from alerts.models import Watchlist
        from listings.selectors import get_listing_by_id
        listing = get_listing_by_id(listing_id=listing_id)
        existing = Watchlist.objects.filter(user=request.user, listing=listing).exists()
        if existing:
            services.remove_from_watchlist(user=request.user, listing_id=listing_id)
            return JsonResponse({'watching': False, 'message': 'İzlemeden çıkarıldı.'})
        else:
            services.add_to_watchlist(user=request.user, listing_id=listing_id)
            return JsonResponse({'watching': True, 'message': 'İzlemeye alındı.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def my_alerts_view(request):
    context = {
        'price_alerts': selectors.get_user_price_alerts(user=request.user),
        'saved_searches': selectors.get_user_saved_searches(user=request.user),
        'watchlist': selectors.get_user_watchlist(user=request.user),
    }
    return render(request, 'alerts/my_alerts.html', context)
```

### alerts/urls.py
```python
from django.urls import path
from alerts import views

app_name = 'alerts'

urlpatterns = [
    path('', views.my_alerts_view, name='my_alerts'),
    path('price-alert/<int:listing_id>/', views.create_price_alert_view, name='create_price_alert'),
    path('price-alert/<int:alert_id>/delete/', views.delete_price_alert_view, name='delete_price_alert'),
    path('save-search/', views.save_search_view, name='save_search'),
    path('save-search/<int:search_id>/delete/', views.delete_saved_search_view, name='delete_saved_search'),
    path('watchlist/<int:listing_id>/', views.toggle_watchlist_view, name='toggle_watchlist'),
]
```

### alerts/admin.py
```python
from django.contrib import admin
from alerts.models import PriceAlert, SavedSearch, Watchlist

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'target_price', 'triggered', 'is_active']
    list_filter = ['triggered', 'is_active']

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'last_checked_at']

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'last_known_price']
```

### babacars/urls.py — add:
```python
path('alerts/', include('alerts.urls', namespace='alerts')),
```

### babacars/middleware.py — add new middleware:
```python
class AlertsCheckMiddleware:
    """
    Checks price alerts, saved searches, watchlist price changes.
    Throttled: runs at most once every 60 seconds per server (via cache timestamp in session).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self._last_run = None

    def __call__(self, request):
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        if self._last_run is None or (now - self._last_run) > timedelta(seconds=60):
            try:
                from alerts.services import check_price_alerts, check_saved_searches, check_watchlist_price_changes
                check_price_alerts()
                check_saved_searches()
                check_watchlist_price_changes()
                self._last_run = now
            except Exception:
                pass
        return self.get_response(request)
```

### settings.py MIDDLEWARE — add after BookingCompletionMiddleware:
```python
'babacars.middleware.AlertsCheckMiddleware',
```

---

## 2. Listing Report (İlan Rapor)

### listings/models.py — add new model:
```python
class ListingReport(models.Model):
    REASON_CHOICES = [
        ('fake', 'Sahte İlan'),
        ('sold', 'Satılmış Araç'),
        ('wrong_info', 'Yanlış Bilgi'),
        ('spam', 'Spam'),
        ('other', 'Diğer'),
    ]
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listing_reports'
        ordering = ['-created_at']
        verbose_name = 'Listing Report'
        verbose_name_plural = 'Listing Reports'

    def __str__(self) -> str:
        return f"Report({self.listing.title} | {self.reason})"
```

### listings/services.py — add:
```python
def report_listing(*, reporter, listing_id: int, reason: str, description: str = '') -> 'ListingReport':
    from listings.models import ListingReport
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if reporter == listing.seller:
        raise PermissionError('Kendi ilanınızı raporlayamazsınız.')
    valid_reasons = ['fake', 'sold', 'wrong_info', 'spam', 'other']
    if reason not in valid_reasons:
        raise ValueError('Geçersiz rapor sebebi.')
    return ListingReport.objects.create(
        listing=listing, reporter=reporter, reason=reason, description=description
    )
```

### listings/views.py — add:
```python
@login_required
@require_http_methods(["POST"])
def report_listing_view(request, listing_id):
    import json
    try:
        data = json.loads(request.body)
        services.report_listing(
            reporter=request.user, listing_id=listing_id,
            reason=data.get('reason'), description=data.get('description', '')
        )
        return JsonResponse({'message': 'İlan raporlandı. Teşekkürler.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)
```

### listings/urls.py — add:
```python
path('<int:listing_id>/report/', views.report_listing_view, name='report'),
```

### listings/admin.py — add:
```python
from listings.models import ListingReport

@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reporter', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    search_fields = ['listing__title']
    actions = ['mark_resolved']

    @admin.action(description='Çözüldü olarak işaretle')
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
```

---

## 3. Vehicle Valuation (Araç Değerleme)

### listings/selectors.py — add:
```python
def get_valuation_data(*, make: str, model: str, year: int) -> dict:
    from django.db.models import Avg, Min, Max, Count
    qs = Listing.objects.filter(
        status='active', listing_type='sale',
        vehicle__make__iexact=make, vehicle__model__iexact=model,
        vehicle__year=year,
    )
    agg = qs.aggregate(
        avg_price=Avg('price'), min_price=Min('price'),
        max_price=Max('price'), count=Count('id'),
    )
    return agg
```

### listings/services.py — add:
```python
def get_vehicle_valuation(*, listing_id: int) -> dict:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    v = listing.vehicle
    data = selectors.get_valuation_data(make=v.make, model=v.model, year=v.year)
    if not data['count'] or data['count'] < 2:
        return {'available': False}
    return {
        'available': True,
        'avg_price': round(float(data['avg_price'])),
        'min_price': round(float(data['min_price'])),
        'max_price': round(float(data['max_price'])),
        'sample_size': data['count'],
        'this_price': float(listing.price),
        'verdict': 'below' if listing.price < data['avg_price'] else 'above',
    }
```

### listings/views.py — add to listing_detail_view context:
```python
# Add to listing_detail_view:
valuation = services.get_vehicle_valuation(listing_id=listing.id)
# Add 'valuation': valuation to context
```

---

## 4. Listing Refresh (İlan Yenileme)

### listings/services.py — add:
```python
def refresh_listing(*, user, listing_id: int) -> 'Listing':
    from django.utils import timezone
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Bu ilanı yenileme yetkiniz yok.')
    if listing.status != 'active':
        raise ValueError('Sadece aktif ilanlar yenilenebilir.')
    listing.created_at = timezone.now()
    listing.save(update_fields=['created_at'])
    return listing
```

### listings/views.py — add:
```python
@login_required
@require_http_methods(["POST"])
def refresh_listing_view(request, listing_id):
    try:
        services.refresh_listing(user=request.user, listing_id=listing_id)
        return JsonResponse({'message': 'İlan yenilendi, en üste taşındı.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)
```

### listings/urls.py — add:
```python
path('<int:listing_id>/refresh/', views.refresh_listing_view, name='refresh'),
```

---

## 5. Bulk Listing Management (Toplu İlan Yönetimi)

### listings/services.py — add:
```python
def bulk_update_status(*, user, listing_ids: list, status: str) -> int:
    valid = ['active', 'passive']
    if status not in valid:
        raise ValueError('Geçersiz durum.')
    listings = Listing.objects.filter(id__in=listing_ids, seller=user)
    listings = listings.exclude(status__in=['sold', 'rented'])
    return listings.update(status=status)
```

### listings/views.py — add:
```python
@login_required
@require_http_methods(["POST"])
def bulk_update_view(request):
    import json
    try:
        data = json.loads(request.body)
        count = services.bulk_update_status(
            user=request.user,
            listing_ids=data.get('listing_ids', []),
            status=data.get('status')
        )
        return JsonResponse({'message': f'{count} ilan güncellendi.', 'count': count})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
```

### listings/urls.py — add:
```python
path('bulk-update/', views.bulk_update_view, name='bulk_update'),
```

---

## 6. Damage Report (Araç Hasar Raporu)

### listings/models.py — add fields to Vehicle model:
```python
# Add to Vehicle model:
has_damage_record = models.BooleanField(default=False)
damage_description = models.TextField(blank=True)
paint_changed_parts = models.PositiveSmallIntegerField(default=0, help_text='Boyalı parça sayısı')
replaced_parts = models.PositiveSmallIntegerField(default=0, help_text='Değişen parça sayısı')
```

### listings/forms.py — add to VehicleForm widgets:
```python
'has_damage_record': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
'damage_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Hasar detayları (varsa)'}),
'paint_changed_parts': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '20'}),
'replaced_parts': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '20'}),
```
And in __init__ set these as not required:
```python
self.fields['has_damage_record'].required = False
self.fields['damage_description'].required = False
self.fields['paint_changed_parts'].required = False
self.fields['replaced_parts'].required = False
```

---

## Migrations
```bash
python manage.py startapp alerts
python manage.py makemigrations alerts listings
python manage.py migrate
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test alerts listings
```
Manually verify:
- Price alert can be created on listing detail
- Saved search saves filters
- Watchlist toggle works
- Listing report submits to admin
- Vehicle valuation shows avg/min/max on detail page
- Listing refresh moves listing to top
- Bulk status update works on dashboard
- Damage fields appear in create form
Expected: 0 errors, 0 failures.
Report any errors before proceeding.

---

## PROMPT

### Context Files (read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- listings_models.md
- notifications_services.md

### Task
Implement all backend features defined above. Token-efficient: copy code blocks exactly, no extra boilerplate.

### Order
1. Create alerts app + models + selectors + services + views + urls + admin
2. Add ListingReport, valuation, refresh, bulk, damage to listings app
3. Add AlertsCheckMiddleware
4. Run migrations
5. Healthcheck

### Rules
1. Copy code blocks exactly. No extra functions.
2. Keyword-only arguments on all service/selector functions.
3. Services raise ValueError/PermissionError; views catch them.
4. All AJAX views return JsonResponse.
5. Middleware throttled to 60s — do not remove the throttle.
6. Run migrations after model changes.
7. Healthcheck before done.

### Output
One code block per file. No explanations.
