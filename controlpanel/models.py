from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Oluşturma'),
        ('update', 'Güncelleme'),
        ('delete', 'Silme'),
        ('login', 'Giriş'),
        ('admin_action', 'Yönetici İşlemi'),
    ]
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self) -> str:
        return f'{self.action} | {self.description}'
