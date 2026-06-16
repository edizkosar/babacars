from django.db.models import QuerySet
from listings.models import Listing, Photo, Favorite, ListingView

def get_listing_by_id(*, listing_id: int) -> Listing:
    return Listing.objects.select_related('vehicle', 'seller').get(id=listing_id)

def get_listing_by_slug(*, slug: str) -> Listing:
    return Listing.objects.select_related('vehicle', 'seller').get(slug=slug)

def get_active_listings() -> QuerySet:
    return Listing.objects.filter(status='active').select_related('vehicle', 'seller').prefetch_related('photos')

def get_listings_by_seller(*, seller) -> QuerySet:
    return Listing.objects.filter(seller=seller).select_related('vehicle').prefetch_related('photos')

def get_photo_by_id(*, photo_id: int) -> Photo:
    return Photo.objects.get(id=photo_id)

def get_photos_by_listing(*, listing) -> QuerySet:
    return Photo.objects.filter(listing=listing).order_by('order')

def get_favorite(*, user, listing) -> Favorite:
    return Favorite.objects.get(user=user, listing=listing)

def get_favorites_by_user(*, user) -> QuerySet:
    return Favorite.objects.filter(user=user).select_related('listing__vehicle')

def get_listing_views(*, listing, days: int = 30) -> QuerySet:
    from django.utils import timezone
    from datetime import timedelta
    since = timezone.now() - timedelta(days=days)
    return ListingView.objects.filter(listing=listing, viewed_at__gte=since)

def search_listings(*, filters: dict) -> QuerySet:
    # filters keys: listing_type, make, model, year_min, year_max,
    #               price_min, price_max, fuel_type, transmission,
    #               body_type, city, ordering
    qs = Listing.objects.filter(status='active').select_related('vehicle').prefetch_related('photos')
    if filters.get('listing_type'):
        qs = qs.filter(listing_type=filters['listing_type'])
    if filters.get('make'):
        qs = qs.filter(vehicle__make__icontains=filters['make'])
    if filters.get('model'):
        qs = qs.filter(vehicle__model__icontains=filters['model'])
    if filters.get('year_min'):
        qs = qs.filter(vehicle__year__gte=filters['year_min'])
    if filters.get('year_max'):
        qs = qs.filter(vehicle__year__lte=filters['year_max'])
    if filters.get('price_min'):
        qs = qs.filter(price__gte=filters['price_min'])
    if filters.get('price_max'):
        qs = qs.filter(price__lte=filters['price_max'])
    if filters.get('fuel_type'):
        qs = qs.filter(vehicle__fuel_type=filters['fuel_type'])
    if filters.get('transmission'):
        qs = qs.filter(vehicle__transmission=filters['transmission'])
    if filters.get('body_type'):
        qs = qs.filter(vehicle__body_type=filters['body_type'])
    if filters.get('city'):
        qs = qs.filter(city__icontains=filters['city'])
    ALLOWED_ORDERING = {'-created_at', 'created_at', 'price', '-price', '-view_count', 'view_count'}
    ordering = filters.get('ordering', '-created_at')
    if ordering not in ALLOWED_ORDERING:
        ordering = '-created_at'
    return qs.order_by(ordering)


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


def get_similar_listings(*, listing, limit: int = 4) -> QuerySet:
    return Listing.objects.filter(
        status='active',
        vehicle__make__iexact=listing.vehicle.make,
    ).exclude(id=listing.id).select_related('vehicle').prefetch_related('photos')[:limit]
