from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

TYPE_CHOICES = [
    ('new_offer', 'New Offer'),
    ('offer_accepted', 'Offer Accepted'),
    ('offer_rejected', 'Offer Rejected'),
    ('offer_countered', 'Offer Countered'),
    ('offer_expired', 'Offer Expired'),
    ('new_message', 'New Message'),
    ('booking_confirmed', 'Booking Confirmed'),
    ('booking_cancelled', 'Booking Cancelled'),
    ('review_received', 'Review Received'),
]


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(choices=TYPE_CHOICES, max_length=30)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def mark_as_read(self):
        # Called from services.py only
        pass

    def __str__(self) -> str:
        return f"Notification({self.recipient.email} | {self.notification_type})"
