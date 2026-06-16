from django.contrib import admin
from listings.models import Listing, Vehicle, Photo, Favorite, ListingView

class VehicleInline(admin.StackedInline):
    model = Vehicle
    extra = 0

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'listing_type', 'status', 'price', 'city', 'created_at']
    list_filter = ['listing_type', 'status', 'city']
    search_fields = ['title', 'seller__email']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    inlines = [VehicleInline, PhotoInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    search_fields = ['user__email', 'listing__title']


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['listing__title', 'user__email']


from listings.models import ListingReport

@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reporter', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    search_fields = ['listing__title']
    actions = ['mark_resolved']

    @admin.action(description='Çözüldü olarak işaretle')
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

