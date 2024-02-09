from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from train_app.models import Stop

@swagger_auto_schema(
    method='POST',
    request_body=StationSerializer, 
    responses={
        201: StationSerializer,
    }
)
@swagger_auto_schema(
    method='GET',
    request_body=None, 
    responses={
        200: StationSerializer(many = True),
    }
)
@api_view(['POST', 'GET'])
def stations_root(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'POST':
        serializer = StationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        stations = []
        for station in Station.objects.order_by('station_id'):
            stations.append(model_to_dict(station))
        return Response({
            'stations': stations
        })


@swagger_auto_schema(
    method='GET',
    request_body=None, 
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
            }
        ),
    }
)
@api_view(['GET'])
def station_trains(request, station_id):
    if not Station.objects.filter(station_id = station_id).exists():
        return Response({
            "message": "station with id: %d was not found" % station_id
        }, status=status.HTTP_404_NOT_FOUND)
    trains = []
    for train in Stop.objects.filter(station_id=station_id).order_by('departure_time', 'arrival_time', 'train_id'):
        trains.append(model_to_dict(train, fields=[
            'train_id',
            'arrival_time',
            'departure_time'
        ]))
    return Response({
        'station_id': station_id,
        'trains': trains
    })