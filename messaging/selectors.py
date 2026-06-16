from django.db.models import QuerySet
from messaging.models import Conversation, Message

def get_conversation_by_id(*, conversation_id: int) -> Conversation:
    return Conversation.objects.select_related('listing', 'buyer', 'seller').get(id=conversation_id)

def get_conversation(*, buyer, listing) -> Conversation:
    return Conversation.objects.get(buyer=buyer, listing=listing)

def get_conversations_by_user(*, user) -> QuerySet:
    from django.db.models import Q
    return Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).select_related('listing', 'buyer', 'seller').order_by('-updated_at')

def get_messages_by_conversation(*, conversation) -> QuerySet:
    return Message.objects.filter(conversation=conversation).order_by('created_at')

def get_message_by_id(*, message_id: int) -> Message:
    return Message.objects.get(id=message_id)

def get_unread_messages(*, user, conversation) -> QuerySet:
    return Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user)
