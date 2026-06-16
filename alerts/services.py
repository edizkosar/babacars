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
