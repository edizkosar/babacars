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
