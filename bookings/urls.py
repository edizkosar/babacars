from django.urls import path
from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('<int:booking_id>/', views.booking_detail_view, name='detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel'),
    path('block/<int:listing_id>/', views.block_dates_view, name='block_dates'),
    path('unblock/<int:unavailable_date_id>/', views.unblock_dates_view, name='unblock_dates'),
    path('availability/<int:listing_id>/', views.check_availability_view, name='check_availability'),
]
