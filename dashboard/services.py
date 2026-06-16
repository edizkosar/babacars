from django.utils import timezone
from datetime import timedelta
from dashboard import selectors
from listings import selectors as listings_selectors
from listings.models import ListingView
from offers.models import Offer
from bookings.models import Booking
from messaging.models import Conversation


def get_dashboard_summary(*, user) -> dict:
    if not user.is_seller():
        raise PermissionError('User is not a seller')

    return {
        'total_listings': selectors.get_seller_listings(seller=user).count(),
        'active_listings': selectors.get_seller_listings(seller=user).filter(status='active').count(),
        'total_views': selectors.get_seller_total_views(seller=user),
        'total_favorites': selectors.get_seller_total_favorites(seller=user),
        'total_offers': Offer.objects.filter(listing__seller=user).count(),
        'pending_offers': selectors.get_seller_pending_offers(seller=user),
        'total_bookings': Booking.objects.filter(listing__seller=user).count(),
        'active_bookings': selectors.get_seller_active_bookings(seller=user),
        'unread_messages': Conversation.objects.filter(
            listing__seller=user, messages__is_read=False
        ).exclude(messages__sender=user).distinct().count(),
    }


def get_listing_stats(*, user, listing_id: int) -> dict:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')

    return {
        'listing_id': listing.id,
        'view_count': selectors.get_listing_view_count(listing=listing),
        'favorite_count': listing.favorite_count,
        'offer_count': selectors.get_listing_offer_count(listing=listing),
        'pending_offer_count': selectors.get_listing_pending_offer_count(listing=listing),
        'message_count': selectors.get_listing_message_count(listing=listing),
        'hourly_traffic': get_hourly_traffic(listing_id=listing.id),
        'daily_traffic': get_daily_traffic(listing_id=listing.id),
    }


def get_hourly_traffic(*, listing_id: int, days: int = 7) -> list:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    since = timezone.now() - timedelta(days=days)
    views = ListingView.objects.filter(listing=listing, viewed_at__gte=since)

    hours = {i: 0 for i in range(24)}
    for v in views:
        hours[timezone.localtime(v.viewed_at).hour] += 1

    return [{'hour': h, 'count': c} for h, c in hours.items()]


def get_daily_traffic(*, listing_id: int, days: int = 30) -> list:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    since = timezone.now() - timedelta(days=days)
    views = ListingView.objects.filter(listing=listing, viewed_at__gte=since)

    dates = {}
    for v in views:
        d = timezone.localtime(v.viewed_at).strftime('%Y-%m-%d')
        dates[d] = dates.get(d, 0) + 1

    return [{'date': d, 'count': c} for d, c in sorted(dates.items())]


def get_offer_conversion_rate(*, listing_id: int) -> float:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    total = selectors.get_listing_offer_count(listing=listing)
    if total == 0:
        return 0.0
    accepted = Offer.objects.filter(listing=listing, status='accepted').count()
    return accepted / total
