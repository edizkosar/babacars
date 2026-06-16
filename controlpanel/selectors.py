from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from listings.models import Listing, ListingView, ListingReport
from offers.models import Offer
from bookings.models import Booking

User = get_user_model()


def get_global_stats() -> dict:
    return {
        'total_users': User.objects.count(),
        'total_sellers': User.objects.filter(role__in=['seller', 'both']).count(),
        'total_listings': Listing.objects.count(),
        'active_listings': Listing.objects.filter(status='active').count(),
        'total_offers': Offer.objects.count(),
        'total_bookings': Booking.objects.count(),
        'total_views': ListingView.objects.count(),
        'pending_reports': ListingReport.objects.filter(is_resolved=False).count(),
    }


def get_recent_users(*, limit: int = 10):
    return User.objects.order_by('-created_at')[:limit]


def get_all_users():
    return User.objects.order_by('-created_at')


def get_all_listings():
    return Listing.objects.select_related('vehicle', 'seller').order_by('-created_at')


def get_all_reports():
    return ListingReport.objects.select_related('listing', 'reporter').order_by('-created_at')


def get_signup_trend(*, days: int = 30):
    since = timezone.now() - timedelta(days=days)
    qs = (User.objects.filter(created_at__gte=since)
          .annotate(d=TruncDate('created_at'))
          .values('d').annotate(c=Count('id')).order_by('d'))
    return list(qs)


def get_listing_trend(*, days: int = 30):
    since = timezone.now() - timedelta(days=days)
    qs = (Listing.objects.filter(created_at__gte=since)
          .annotate(d=TruncDate('created_at'))
          .values('d').annotate(c=Count('id')).order_by('d'))
    return list(qs)


def get_top_cities(*, limit: int = 5):
    qs = (Listing.objects.values('city')
          .annotate(c=Count('id')).order_by('-c')[:limit])
    return list(qs)


def get_most_viewed_listings(*, limit: int = 5):
    return Listing.objects.order_by('-view_count')[:limit]


def get_status_distribution() -> list:
    qs = (Listing.objects.values('status')
          .annotate(c=Count('id')).order_by('-c'))
    return list(qs)


def get_top_sellers(*, limit: int = 5):
    qs = (User.objects.filter(role__in=['seller', 'both'])
          .annotate(listing_count=Count('listings'))
          .order_by('-listing_count')[:limit])
    return qs


def get_system_summary() -> dict:
    sale_qs = Listing.objects.filter(listing_type='sale', status='active')
    agg = sale_qs.aggregate(avg=Avg('price'))
    most_expensive = sale_qs.order_by('-price').first()
    cheapest = sale_qs.order_by('price').first()
    top_make = (Listing.objects.values('vehicle__make')
                .annotate(c=Count('id')).order_by('-c').first())
    return {
        'avg_price': round(float(agg['avg'])) if agg['avg'] else 0,
        'most_expensive': most_expensive,
        'cheapest': cheapest,
        'top_make': top_make['vehicle__make'] if top_make else '-',
        'top_make_count': top_make['c'] if top_make else 0,
    }


def get_recent_activity(*, limit: int = 15) -> list:
    # Combines recent users, listings, offers into one activity feed
    activity = []
    for u in User.objects.order_by('-created_at')[:limit]:
        activity.append({'type': 'user', 'text': f'{u.email} kayıt oldu', 'time': u.created_at})
    for l in Listing.objects.select_related('seller').order_by('-created_at')[:limit]:
        activity.append({'type': 'listing', 'text': f'{l.seller.email} "{l.title}" ilanını ekledi', 'time': l.created_at})
    for o in Offer.objects.select_related('buyer', 'listing').order_by('-created_at')[:limit]:
        activity.append({'type': 'offer', 'text': f'{o.buyer.email} {o.listing.title} için {o.amount} TL teklif verdi', 'time': o.created_at})
    activity.sort(key=lambda x: x['time'], reverse=True)
    return activity[:limit]


def get_activity_logs(*, limit: int = 50):
    from controlpanel.models import ActivityLog
    return ActivityLog.objects.select_related('actor')[:limit]
