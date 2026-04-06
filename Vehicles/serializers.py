from rest_framework import serializers
from .models import Vehicle, VehicleImage

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['image']

class VehicleSerializer(serializers.ModelSerializer):
    # This includes the images inside the vehicle JSON
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'year', 'mileage', 
            'transmission', 'fuel_type', 'price', 
            'gps_coor', 'is_rental', 'desc', 'images'
        ]