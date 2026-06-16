from django.db.models import QuerySet
from notifications.models import Notification

def get_notification_by_id(*, notification_id: int) -> Notification:
    return Notification.objects.get(id=notification_id)

def get_notifications_by_user(*, user) -> QuerySet:
    return Notification.objects.filter(recipient=user).order_by('-created_at')

def get_unread_notifications(*, user) -> QuerySet:
    return Notification.objects.filter(recipient=user, is_read=False)
