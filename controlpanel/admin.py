from django.contrib import admin
from controlpanel.models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'actor', 'description', 'created_at']
    list_filter = ['action']
    search_fields = ['description', 'actor__email']
