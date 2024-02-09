from rest_framework import serializers
from .models import Station
from drf_yasg import openapi

class StationSerializer(serializers.ModelSerializer):
    station_id = serializers.IntegerField()
    class Meta():
        model = Station
        fields = "__all__"


    def create(self, validated_data):
        return Station.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.station_id = validated_data.get('station_id', instance.station_id)
        instance.station_name = validated_data.get('station_name', instance.station_name)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.save()
        return instance

StationNotFound = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(
            type=openapi.TYPE_STRING
        )
    }
)