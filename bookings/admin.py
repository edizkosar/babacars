from django.contrib import admin
from bookings.models import Booking, UnavailableDate

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'renter', 'start_date', 'end_date', 'total_price', 'status']
    list_filter = ['status']
    search_fields = ['listing__title', 'renter__email']
    ordering = ['-created_at']


@admin.register(UnavailableDate)
class UnavailableDateAdmin(admin.ModelAdmin):
    list_display = ['listing', 'start_date', 'end_date', 'reason']
    list_filter = ['reason']
    search_fields = ['listing__title']
