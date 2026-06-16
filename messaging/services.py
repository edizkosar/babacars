from django.utils import timezone
from messaging.models import Conversation, Message
from messaging import selectors
from notifications.services import create_notification
from listings import selectors as listings_selectors

def get_or_create_conversation(*, buyer, listing_id: int) -> Conversation:
    listing = listings_selectors.get_listing_by_id(listing_id=listing_id)
    if listing.status not in ['active']:
        raise ValueError('Listing is not active')
    if buyer == listing.seller:
        raise PermissionError('Seller cannot initiate conversation')
        
    try:
        return selectors.get_conversation(buyer=buyer, listing=listing)
    except Conversation.DoesNotExist:
        return Conversation.objects.create(
            listing=listing,
            buyer=buyer,
            seller=listing.seller
        )

def send_message(*, sender, conversation_id: int, body: str) -> Message:
    conversation = selectors.get_conversation_by_id(conversation_id=conversation_id)
    if sender not in [conversation.buyer, conversation.seller]:
        raise PermissionError('Not authorized')
    if not body or not body.strip():
        raise ValueError('Message body cannot be empty')
    if not conversation.is_active:
        raise ValueError('Conversation is closed')
        
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        body=body
    )
    
    # auto_now updates updated_at automatically on Conversation? No, we must call save.
    conversation.save()
    
    recipient = conversation.get_other_participant(sender)
    create_notification(
        recipient=recipient,
        notification_type='new_message',
        title=f'Yeni Mesaj: {conversation.listing.title}',
        related_object=message
    )
    
    return message

def mark_messages_as_read(*, user, conversation_id: int) -> int:
    conversation = selectors.get_conversation_by_id(conversation_id=conversation_id)
    if user not in [conversation.buyer, conversation.seller]:
        raise PermissionError('Not authorized')
        
    unread_messages = selectors.get_unread_messages(user=user, conversation=conversation)
    count = unread_messages.update(is_read=True, read_at=timezone.now())
    return count

def delete_message(*, user, message_id: int) -> Message:
    message = selectors.get_message_by_id(message_id=message_id)
    if user != message.sender:
        raise PermissionError('Not authorized')
    if message.is_deleted:
        raise ValueError('Message already deleted')
        
    message.body = 'Bu mesaj silindi.'
    message.is_deleted = True
    message.save(update_fields=['body', 'is_deleted'])
    return message

def close_conversation(*, user, conversation_id: int) -> Conversation:
    conversation = selectors.get_conversation_by_id(conversation_id=conversation_id)
    if user not in [conversation.buyer, conversation.seller]:
        raise PermissionError('Not authorized')
        
    conversation.is_active = False
    conversation.save(update_fields=['is_active'])
    return conversation
