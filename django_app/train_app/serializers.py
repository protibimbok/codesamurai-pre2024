from rest_framework import serializers
from .models import Train, Stop
from drf_yasg import openapi


class StopSerializer(serializers.ModelSerializer):
    train_id = serializers.IntegerField(required = False)
    station_id = serializers.IntegerField()
    class Meta():
        model = Stop
        fields = '__all__'

    def create(self, validated_data):
        return Stop.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.stop_id = validated_data.get('stop_id', instance.stop_id)
        instance.train_id = validated_data.get('train_id', instance.train_id)
        instance.station_id = validated_data.get('station_id', instance.station_id)
        instance.arrival_time = validated_data.get('arrival_time', instance.arrival_time)
        instance.departure_time = validated_data.get('departure_time', instance.departure_time)
        instance.fare = validated_data.get('fare', instance.fare)
        instance.save()
        return instance


class TrainSerializer(serializers.ModelSerializer):
    train_id = serializers.IntegerField()
    stops = StopSerializer(many = True)
    class Meta():
        model = Train
        fields = "__all__"


    def create(self, validated_data):
        del validated_data['stops']
        return Train.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.train_id = validated_data.get('train_id', instance.train_id)
        instance.train_name = validated_data.get('train_name', instance.train_name)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.save()
        return instance
    
TrainAddedResponse = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={}
)

TrainNotFound = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(
            type=openapi.TYPE_STRING
        )
    }
)