from django.utils import timezone
from notifications.models import Notification, TYPE_CHOICES
from notifications import selectors
from django.contrib.contenttypes.models import ContentType

def create_notification(*, recipient, notification_type: str, title: str, body: str = '', related_object=None) -> Notification:
    valid_types = [choice[0] for choice in TYPE_CHOICES]
    if notification_type not in valid_types:
        raise ValueError(f'Invalid notification type: {notification_type}')
    if recipient is None:
        raise ValueError('Recipient cannot be None')
        
    notification = Notification(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        body=body
    )
    
    if related_object:
        notification.content_type = ContentType.objects.get_for_model(related_object)
        notification.object_id = related_object.pk
        
    notification.save()
    return notification

def mark_as_read(*, user, notification_id: int) -> Notification:
    notification = selectors.get_notification_by_id(notification_id=notification_id)
    if user != notification.recipient:
        raise PermissionError('Not authorized')
    if notification.is_read:
        raise ValueError('Notification already read')
        
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=['is_read', 'read_at'])
    return notification

def mark_all_as_read(*, user) -> int:
    unread = selectors.get_unread_notifications(user=user)
    count = unread.update(is_read=True, read_at=timezone.now())
    return count

def get_unread_count(*, user) -> int:
    return selectors.get_unread_notifications(user=user).count()
