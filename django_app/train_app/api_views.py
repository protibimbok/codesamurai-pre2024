from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import Stop, Train
from station_app.models import Station


@swagger_auto_schema(
    method='POST',
    request_body=TrainSerializer, 
    responses={
        201: TrainAddedResponse,
    }
)
@api_view(['POST'])
@transaction.atomic
def trains_root(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'POST':
        serializer = TrainSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.data
        stops = data['stops']
        del data['stops']
        train = Train.objects.create(**data)
        for stop in stops:
            stop['train_id'] = train
            stop['station_id'] = Station(station_id = stop['station_id'])
            Stop.objects.create(**stop)
        
        num_stations = len(stops)
        start_time = end_time = ''
        if num_stations > 0:
            start_time = stops[0]['departure_time']
            end_time = stops[num_stations - 1]['departure_time']

        return Response({
            **data,
            'service_start': start_time,
            'service_end': end_time,
            'num_stations': num_stations
        }, status=status.HTTP_201_CREATED)


