from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='list'),
    path('<int:notification_id>/read/', views.mark_as_read_view, name='mark_as_read'),
    path('read-all/', views.mark_all_as_read_view, name='mark_all_as_read'),
    path('unread-count/', views.unread_count_view, name='unread_count'),
]
