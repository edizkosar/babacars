from django.db.models import QuerySet
from offers.models import Offer

def get_offer_by_id(*, offer_id: int) -> Offer:
    return Offer.objects.select_related('listing', 'buyer').get(id=offer_id)

def get_offers_by_listing(*, listing) -> QuerySet:
    return Offer.objects.filter(listing=listing).select_related('buyer').order_by('-created_at')

def get_offers_by_buyer(*, buyer) -> QuerySet:
    return Offer.objects.filter(buyer=buyer).select_related('listing').order_by('-created_at')

def get_pending_offer(*, buyer, listing) -> Offer:
    return Offer.objects.get(buyer=buyer, listing=listing, status='pending')

def get_expired_offers() -> QuerySet:
    from django.utils import timezone
    return Offer.objects.filter(status='pending', expires_at__lte=timezone.now())

def get_offer_chain(*, root_offer) -> QuerySet:
    # Returns all offers in chain starting from root
    ids = []
    current = root_offer
    while current is not None:
        ids.append(current.id)
        current = Offer.objects.filter(parent_offer=current).first()
    return Offer.objects.filter(id__in=ids).order_by('created_at')
