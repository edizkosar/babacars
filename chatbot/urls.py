from django.urls import path
from chatbot import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
]
