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
