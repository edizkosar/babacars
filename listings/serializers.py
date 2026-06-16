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
