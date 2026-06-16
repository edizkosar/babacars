from django.urls import path
from messaging import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('start/<int:listing_id>/', views.start_conversation_view, name='start'),
    path('<int:conversation_id>/send/', views.send_message_view, name='send'),
    path('message/<int:message_id>/delete/', views.delete_message_view, name='delete_message'),
    path('<int:conversation_id>/close/', views.close_conversation_view, name='close'),
]
