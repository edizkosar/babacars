from django.contrib import admin
from messaging.models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'body', 'is_read', 'created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'seller', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['listing__title', 'buyer__email', 'seller__email']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'is_read', 'is_deleted', 'created_at']
    list_filter = ['is_read', 'is_deleted']
    search_fields = ['sender__email']
