from django.contrib import admin
from alerts.models import PriceAlert, SavedSearch, Watchlist

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'target_price', 'triggered', 'is_active']
    list_filter = ['triggered', 'is_active']

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'last_checked_at']

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'last_known_price']
