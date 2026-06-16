from django.db import models
from django.conf import settings
from listings.models import Listing

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('countered', 'Countered'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]


class Offer(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_offers',
    )
    parent_offer = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='counter_offers',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    message = models.TextField(blank=True)
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offers'
        ordering = ['-created_at']
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def is_rental_offer(self) -> bool:
        return self.rental_start_date is not None

    def is_root_offer(self) -> bool:
        return self.parent_offer is None

    def get_chain(self):
        # Returns full offer chain from root to this offer
        chain = []
        current = self
        while current is not None:
            chain.append(current)
            current = current.parent_offer
        return list(reversed(chain))

    def __str__(self) -> str:
        return f"Offer({self.buyer.email} → {self.listing.title} | {self.amount} {self.currency})"
