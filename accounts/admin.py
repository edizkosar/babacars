from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User, SellerProfile, Review

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'email_verified', 'is_active', 'created_at']
    list_filter = ['role', 'email_verified', 'is_active']
    search_fields = ['email', 'phone']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BabaCars', {'fields': ('role', 'phone', 'avatar', 'email_verified')}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'id_verified', 'total_sales', 'rating']
    list_filter = ['is_verified', 'id_verified']
    search_fields = ['user__email']
    actions = ['verify_sellers']

    @admin.action(description='Seçili satıcıları doğrula')
    def verify_sellers(self, request, queryset):
        queryset.update(is_verified=True)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'seller', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['reviewer__email', 'seller__user__email']
