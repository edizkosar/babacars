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
