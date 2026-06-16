from bookings.models import Booking, UnavailableDate
from bookings import selectors
from notifications.services import create_notification
from listings import selectors as listings_selectors

def create_booking_from_offer(*, offer) -> Booking:
    if offer.listing.listing_type != 'rental':
        raise ValueError('Listing is not a rental')
        
    if not check_availability(
        listing_id=offer.listing.id, 
        start_date=offer.rental_start_date, 
        end_date=offer.rental_end_date
    ):
        raise ValueError('Selected dates are no longer available')
        
    total_price = calculate_total_price(offer=offer)
    
    booking = Booking.objects.create(
        listing=offer.listing,
        renter=offer.buyer,
        offer=offer,
        start_date=offer.rental_start_date,
        end_date=offer.rental_end_date,
        total_price=total_price,
        status='confirmed'
    )
    
    UnavailableDate.objects.create(
        listing=offer.listing,
        start_date=offer.rental_start_date,
        end_date=offer.rental_end_date,
        reason='booked'
    )
    
    listing = offer.listing
    listing.status = 'rented'
    listing.save(update_fields=['status'])
    
    create_notification(
        recipient=offer.buyer,
        notification_type='booking_confirmed',
        title=f'Rezervasyon Onaylandı: {listing.title}',
        related_object=booking
    )
    
    return booking

def cancel_booking(*, user, booking_id: int) -> Booking:
    booking = selectors.get_booking_by_id(booking_id=booking_id)
    if user != booking.renter and user != booking.listing.seller:
        raise PermissionError('Not authorized')
    if booking.status == 'completed':
        raise ValueError('Cannot cancel a completed booking')
        
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    
    UnavailableDate.objects.filter(
        listing=booking.listing,
        start_date=booking.start_date,
        end_date=booking.end_date,
        reason='booked'
    ).delete()
    
    listing = booking.listing
    listing.status = 'active'
    listing.save(update_fields=['status'])
    
    create_notification(
        recipient=booking.renter,
        notification_type='booking_cancelled',
        title=f'Rezervasyon İptal Edildi: {listing.title}',
        related_object=booking
    )
    create_notification(
        recipient=booking.listing.seller,
        notification_type='booking_cancelled',
        title=f'Rezervasyon İptal Edildi: {listing.title}',
        related_object=booking
    )
    
    return booking

def complete_booking(*, booking_id: int) -> Booking:
    booking = selectors.get_booking_by_id(booking_id=booking_id)
    if booking.status != 'active':
        raise ValueError('Only active bookings can be completed')
        
    booking.status = 'completed'
    booking.save(update_fields=['status'])
    
    listing = booking.listing
    listing.status = 'active'
    listing.save(update_fields=['status'])
    
    return booking

def check_availability(*, listing_id: int, start_date, end_date) -> bool:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    unavailable_dates = selectors.get_unavailable_dates(listing=listing)
    
    for unavail in unavailable_dates:
        if start_date < unavail.end_date and end_date > unavail.start_date:
            return False
    return True

def block_dates(*, user, listing_id: int, start_date, end_date, reason: str = 'blocked') -> UnavailableDate:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')
    if reason not in ['maintenance', 'blocked']:
        raise ValueError('Invalid reason')
        
    if not check_availability(listing_id=listing_id, start_date=start_date, end_date=end_date):
        raise ValueError('Dates overlap with existing unavailable dates')
        
    return UnavailableDate.objects.create(
        listing=listing,
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )

def unblock_dates(*, user, unavailable_date_id: int) -> None:
    unavail = selectors.get_unavailable_date_by_id(unavailable_date_id=unavailable_date_id)
    if user != unavail.listing.seller:
        raise PermissionError('Not authorized')
    if unavail.reason == 'booked':
        raise ValueError('Cannot unblock a confirmed booking')
        
    unavail.delete()

def calculate_total_price(*, offer) -> float:
    duration_days = (offer.rental_end_date - offer.rental_start_date).days
    base_price = float(offer.listing.price)  # Use listing price per spec
    
    if duration_days <= 6:
        return base_price * duration_days
    elif 7 <= duration_days <= 29:
        return base_price * duration_days * 0.90
    elif 30 <= duration_days <= 364:
        return base_price * duration_days * 0.80
    else:
        return base_price * duration_days * 0.70
