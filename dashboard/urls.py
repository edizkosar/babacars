from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('listing/<int:listing_id>/', views.listing_stats_view, name='listing_stats'),
    path('listing/<int:listing_id>/traffic/', views.listing_traffic_view, name='listing_traffic'),
]
