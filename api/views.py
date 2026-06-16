from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from listings.models import Listing
from listings.serializers import ListingSerializer
from offers.serializers import OfferSerializer
from bookings.serializers import BookingSerializer, UnavailableDateSerializer
from listings import selectors as listing_selectors
from offers import selectors as offer_selectors
from bookings import selectors as booking_selectors


class ListingListAPIView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        filters = {
            'listing_type': self.request.query_params.get('listing_type'),
            'make': self.request.query_params.get('make'),
            'model': self.request.query_params.get('model'),
            'city': self.request.query_params.get('city'),
            'price_min': self.request.query_params.get('price_min'),
            'price_max': self.request.query_params.get('price_max'),
            'ordering': self.request.query_params.get('ordering', '-created_at'),
        }
        return listing_selectors.search_listings(filters={k: v for k, v in filters.items() if v})


class ListingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    lookup_field = 'slug'

    def get_queryset(self):
        return Listing.objects.filter(status='active').select_related('vehicle', 'seller')


class OfferListAPIView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        return offer_selectors.get_offers_by_buyer(buyer=self.request.user)


class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        return booking_selectors.get_bookings_by_renter(renter=self.request.user)


class UnavailableDateListAPIView(generics.ListAPIView):
    serializer_class = UnavailableDateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        listing_id = self.kwargs['listing_id']
        listing = Listing.objects.get(id=listing_id)
        return booking_selectors.get_unavailable_dates(listing=listing)
