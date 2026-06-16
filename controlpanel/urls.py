from django.urls import path
from controlpanel import views

app_name = 'controlpanel'

urlpatterns = [
    path('', views.panel_home_view, name='home'),
    path('users/', views.panel_users_view, name='users'),
    path('listings/', views.panel_listings_view, name='listings'),
    path('reports/', views.panel_reports_view, name='reports'),
    path('activity/', views.panel_activity_view, name='activity'),
    path('charts-data/', views.panel_charts_data_view, name='charts_data'),
    path('users/<int:user_id>/toggle/', views.toggle_user_view, name='toggle_user'),
    path('users/<int:user_id>/verify/', views.verify_seller_view, name='verify_seller'),
    path('listings/<int:listing_id>/delete/', views.delete_listing_view, name='delete_listing'),
    path('listings/<int:listing_id>/status/', views.set_listing_status_view, name='set_status'),
    path('reports/<int:report_id>/resolve/', views.resolve_report_view, name='resolve_report'),
]
