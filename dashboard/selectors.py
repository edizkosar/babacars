from django.db.models import QuerySet
from listings.models import Listing, ListingView, Favorite
from offers.models import Offer
from bookings.models import Booking
from messaging.models import Conversation

def get_seller_listings(*, seller) -> QuerySet:
    return Listing.objects.filter(seller=seller).select_related('vehicle').prefetch_related('photos')

def get_listing_view_count(*, listing) -> int:
    return ListingView.objects.filter(listing=listing).count()

def get_listing_offer_count(*, listing) -> int:
    return Offer.objects.filter(listing=listing).count()

def get_listing_pending_offer_count(*, listing) -> int:
    return Offer.objects.filter(listing=listing, status='pending').count()

def get_listing_message_count(*, listing) -> int:
    return Conversation.objects.filter(listing=listing).count()

def get_seller_total_views(*, seller) -> int:
    return ListingView.objects.filter(listing__seller=seller).count()

def get_seller_total_favorites(*, seller) -> int:
    return Favorite.objects.filter(listing__seller=seller).count()

def get_seller_pending_offers(*, seller) -> int:
    return Offer.objects.filter(listing__seller=seller, status='pending').count()

def get_seller_active_bookings(*, seller) -> int:
    return Booking.objects.filter(listing__seller=seller, status='confirmed').count()
