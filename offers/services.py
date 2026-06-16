from django.utils import timezone
from datetime import timedelta
from offers.models import Offer
from offers import selectors
from notifications.services import create_notification
from listings import selectors as listings_selectors

def create_offer(*, buyer, listing_id: int, amount: float, message: str = '', rental_start_date=None, rental_end_date=None) -> Offer:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    if listing.status not in ['active']:
        raise ValueError('Listing is not active')
    if buyer == listing.seller:
        raise PermissionError('Cannot make an offer on your own listing')
        
    if listing.listing_type == 'rental' and (rental_start_date is None or rental_end_date is None):
        raise ValueError('Rental dates are required for rental listings')
    if rental_start_date and rental_end_date and rental_end_date <= rental_start_date:
        raise ValueError('End date must be after start date')
        
    try:
        selectors.get_pending_offer(buyer=buyer, listing=listing)
        raise ValueError('You already have a pending offer on this listing')
    except Offer.DoesNotExist:
        pass
        
    if amount <= 0:
        raise ValueError('Amount must be greater than 0')
        
    offer = Offer.objects.create(
        listing=listing,
        buyer=buyer,
        amount=amount,
        message=message,
        rental_start_date=rental_start_date,
        rental_end_date=rental_end_date,
        expires_at=timezone.now() + timedelta(days=30)
    )
    
    create_notification(
        recipient=listing.seller,
        notification_type='new_offer',
        title=f'Yeni Teklif: {listing.title}',
        related_object=offer
    )
    return offer

def accept_offer(*, user, offer_id: int) -> Offer:
    offer = selectors.get_offer_by_id(offer_id=offer_id)
    listing = offer.listing
    if user != listing.seller:
        raise PermissionError('Not authorized')
    if offer.status != 'pending':
        raise ValueError('Offer is not pending')
        
    offer.status = 'accepted'
    offer.save(update_fields=['status'])
    
    cancel_other_offers(listing=listing, exclude_offer_id=offer.id)
    
    if listing.listing_type == 'rental':
        from bookings.services import create_booking_from_offer
        create_booking_from_offer(offer=offer)
    else:
        listing.status = 'sold'
        listing.save(update_fields=['status'])
        
    create_notification(
        recipient=offer.buyer,
        notification_type='offer_accepted',
        title=f'Teklifiniz Kabul Edildi: {listing.title}',
        related_object=offer
    )
    return offer

def reject_offer(*, user, offer_id: int) -> Offer:
    offer = selectors.get_offer_by_id(offer_id=offer_id)
    if user != offer.listing.seller:
        raise PermissionError('Not authorized')
    if offer.status != 'pending':
        raise ValueError('Offer is not pending')
        
    offer.status = 'rejected'
    offer.save(update_fields=['status'])
    
    create_notification(
        recipient=offer.buyer,
        notification_type='offer_rejected',
        title=f'Teklifiniz Reddedildi: {offer.listing.title}',
        related_object=offer
    )
    return offer

def counter_offer(*, user, offer_id: int, amount: float, message: str = '') -> Offer:
    offer = selectors.get_offer_by_id(offer_id=offer_id)
    if user != offer.listing.seller:
        raise PermissionError('Not authorized')
    if offer.status != 'pending':
        raise ValueError('Offer is not pending')
    if amount <= 0:
        raise ValueError('Amount must be greater than 0')
        
    offer.status = 'countered'
    offer.save(update_fields=['status'])
    
    new_offer = Offer.objects.create(
        listing=offer.listing,
        buyer=offer.buyer,
        parent_offer=offer,
        amount=amount,
        message=message,
        rental_start_date=offer.rental_start_date,
        rental_end_date=offer.rental_end_date,
        expires_at=timezone.now() + timedelta(days=30)
    )
    
    create_notification(
        recipient=new_offer.buyer,
        notification_type='offer_countered',
        title=f'Karşı Teklif Geldi: {offer.listing.title}',
        related_object=new_offer
    )
    return new_offer

def cancel_offer(*, user, offer_id: int) -> Offer:
    offer = selectors.get_offer_by_id(offer_id=offer_id)
    if user != offer.buyer:
        raise PermissionError('Not authorized')
    if offer.status != 'pending':
        raise ValueError('Offer is not pending')
        
    offer.status = 'cancelled'
    offer.save(update_fields=['status'])
    return offer

def expire_stale_offers() -> int:
    expired_offers = selectors.get_expired_offers()
    count = 0
    for offer in expired_offers:
        offer.status = 'expired'
        offer.save(update_fields=['status'])
        
        create_notification(
            recipient=offer.buyer,
            notification_type='offer_expired',
            title=f'Teklif Süresi Doldu: {offer.listing.title}',
            related_object=offer
        )
        create_notification(
            recipient=offer.listing.seller,
            notification_type='offer_expired',
            title=f'Teklif Süresi Doldu: {offer.listing.title}',
            related_object=offer
        )
        count += 1
    return count

def cancel_other_offers(*, listing, exclude_offer_id: int) -> None:
    other_offers = Offer.objects.filter(
        listing=listing, 
        status__in=['pending', 'countered']
    ).exclude(id=exclude_offer_id)
    
    for offer in other_offers:
        offer.status = 'cancelled'
        offer.save(update_fields=['status'])
