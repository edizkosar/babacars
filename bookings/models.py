from django.db import models
from django.conf import settings
from listings.models import Listing
from offers.models import Offer

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

REASON_CHOICES = [
    ('booked', 'Booked'),
    ('maintenance', 'Maintenance'),
    ('blocked', 'Blocked by Seller'),
]


class Booking(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    offer = models.OneToOneField(
        Offer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days

    def __str__(self) -> str:
        return f"Booking({self.renter.email} → {self.listing.title} | {self.start_date} – {self.end_date})"


class UnavailableDate(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='unavailable_dates',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(choices=REASON_CHOICES, max_length=20, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'unavailable_dates'
        verbose_name = 'Unavailable Date'
        verbose_name_plural = 'Unavailable Dates'

    def __str__(self) -> str:
        return f"Unavailable({self.listing.title} | {self.start_date} – {self.end_date})"
