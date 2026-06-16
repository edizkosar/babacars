from django.db import models
from django.conf import settings


class PriceAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_alerts')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='price_alerts')
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'price_alerts'
        unique_together = ('user', 'listing')
        verbose_name = 'Price Alert'
        verbose_name_plural = 'Price Alerts'

    def __str__(self) -> str:
        return f"PriceAlert({self.user.email} → {self.listing.title} @ {self.target_price})"


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters_json = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_searches'
        ordering = ['-created_at']
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'

    def __str__(self) -> str:
        return f"SavedSearch({self.user.email} | {self.name})"


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='watched_by')
    last_known_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'listing')
        verbose_name = 'Watchlist Item'
        verbose_name_plural = 'Watchlist Items'

    def __str__(self) -> str:
        return f"Watchlist({self.user.email} → {self.listing.title})"
