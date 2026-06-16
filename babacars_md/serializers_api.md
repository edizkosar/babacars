# serializers_api.md

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See listings_models.md, offers_models.md, bookings_models.md for model definitions.

## Purpose
DRF serializers and API views for REST API endpoints.
Endpoint prefix: /api/v1/
Auth: Session-based + Token auth.

## Dependencies
```python
from rest_framework import serializers, generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
```

---

## listings/serializers.py

```python
from rest_framework import serializers
from listings.models import Listing, Vehicle, Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'is_cover', 'order']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'make', 'model', 'year', 'mileage', 'fuel_type',
            'transmission', 'body_type', 'color', 'horsepower',
            'torque', 'trunk_volume', 'fuel_consumption'
        ]


class ListingSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'slug', 'title', 'listing_type', 'status',
            'price', 'currency', 'city', 'district',
            'view_count', 'favorite_count', 'created_at',
            'seller_email', 'vehicle', 'photos'
        ]
```

---

## offers/serializers.py

```python
from rest_framework import serializers
from offers.models import Offer

class OfferSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'listing', 'listing_title', 'buyer_email',
            'amount', 'currency', 'status', 'message',
            'rental_start_date', 'rental_end_date',
            'expires_at', 'created_at'
        ]
        read_only_fields = ['status', 'expires_at', 'created_at']
```

---

## bookings/serializers.py

```python
from rest_framework import serializers
from bookings.models import Booking, UnavailableDate

class BookingSerializer(serializers.ModelSerializer):
    renter_email = serializers.EmailField(source='renter.email', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'renter_email',
            'start_date', 'end_date', 'total_price',
            'currency', 'status', 'created_at'
        ]
        read_only_fields = ['total_price', 'status', 'created_at']


class UnavailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnavailableDate
        fields = ['id', 'start_date', 'end_date', 'reason']
```

---

## api/views.py

```python
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from listings.models import Listing
from offers.models import Offer
from bookings.models import Booking, UnavailableDate
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
```

---

## api/urls.py

```python
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
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test api
```
Manually verify in browser:
- GET /api/v1/listings/ returns JSON list
- GET /api/v1/listings/<slug>/ returns JSON detail
- GET /api/v1/offers/ returns 401 for unauthenticated
- GET /api/v1/bookings/ returns 401 for unauthenticated
- GET /api/v1/listings/<id>/unavailable-dates/ returns JSON list
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- listings_models.md
- offers_models.md
- bookings_models.md
- selectors.md

### Task
Implement all serializer and API files exactly as defined in this document.

### Files to Create
- listings/serializers.py
- offers/serializers.py
- bookings/serializers.py
- api/views.py
- api/urls.py

### Rules
1. Serialization only in serializers.py. No business logic.
2. API views use selectors.py for all queries. Never write ORM queries in views.
3. ListingListAPIView supports query param filtering via listing_selectors.search_listings.
4. Authentication: SessionAuthentication + TokenAuthentication on all views.
5. Public endpoints: listing list, listing detail, unavailable dates.
6. Protected endpoints: offers, bookings (IsAuthenticated).
7. Run Healthcheck after all files are created.

### Output
One code block per file. No explanations.
