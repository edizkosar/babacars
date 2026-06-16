from django.urls import path
from offers import views

app_name = 'offers'

urlpatterns = [
    path('create/<int:listing_id>/', views.create_offer_view, name='create'),
    path('<int:offer_id>/accept/', views.accept_offer_view, name='accept'),
    path('<int:offer_id>/reject/', views.reject_offer_view, name='reject'),
    path('<int:offer_id>/counter/', views.counter_offer_view, name='counter'),
    path('<int:offer_id>/cancel/', views.cancel_offer_view, name='cancel'),
    path('my-offers/', views.my_offers_view, name='my_offers'),
    path('listing/<int:listing_id>/', views.listing_offers_view, name='listing_offers'),
]
