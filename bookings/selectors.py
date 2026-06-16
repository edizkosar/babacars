from django.db.models import QuerySet
from bookings.models import Booking, UnavailableDate

def get_booking_by_id(*, booking_id: int) -> Booking:
    return Booking.objects.select_related('listing', 'renter').get(id=booking_id)

def get_bookings_by_renter(*, renter) -> QuerySet:
    return Booking.objects.filter(renter=renter).select_related('listing').order_by('-created_at')

def get_bookings_by_listing(*, listing) -> QuerySet:
    return Booking.objects.filter(listing=listing).select_related('renter').order_by('-created_at')

def get_active_bookings() -> QuerySet:
    from django.utils import timezone
    return Booking.objects.filter(status='confirmed', end_date__lt=timezone.now().date())

def get_unavailable_dates(*, listing) -> QuerySet:
    return UnavailableDate.objects.filter(listing=listing)

def get_unavailable_date_by_id(*, unavailable_date_id: int) -> UnavailableDate:
    return UnavailableDate.objects.get(id=unavailable_date_id)
