from django.urls import path
from alerts import views

app_name = 'alerts'

urlpatterns = [
    path('', views.my_alerts_view, name='my_alerts'),
    path('price-alert/<int:listing_id>/', views.create_price_alert_view, name='create_price_alert'),
    path('price-alert/<int:alert_id>/delete/', views.delete_price_alert_view, name='delete_price_alert'),
    path('save-search/', views.save_search_view, name='save_search'),
    path('save-search/<int:search_id>/delete/', views.delete_saved_search_view, name='delete_saved_search'),
    path('watchlist/<int:listing_id>/', views.toggle_watchlist_view, name='toggle_watchlist'),
]
