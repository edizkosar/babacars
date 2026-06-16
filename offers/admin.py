from django.contrib import admin
from offers.models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'amount', 'status', 'expires_at', 'created_at']
    list_filter = ['status']
    search_fields = ['listing__title', 'buyer__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
