from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('listings/', views.ListingListAPIView.as_view(), name='listing_list'),
    path('listings/<slug:slug>/', views.ListingDetailAPIView.as_view(), name='listing_detail'),
    path('offers/', views.OfferListAPIView.as_view(), name='offer_list'),
    path('bookings/', views.BookingListAPIView.as_view(), name='booking_list'),
    path('listings/<int:listing_id>/unavailable-dates/', views.UnavailableDateListAPIView.as_view(), name='unavailable_dates'),
]
