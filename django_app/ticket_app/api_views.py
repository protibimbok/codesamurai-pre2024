from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from train_app.models import Stop
from users_app.models import *
from station_app.models import *
from .algo.purchase_ticket import purchase_ticket_main


@swagger_auto_schema(
    method='POST',
    request_body=TicketPurchase, 
    responses={
        201: openapi.Schema(type= openapi.TYPE_OBJECT, properties={}),
    }
)
@api_view(['POST'])
def purchase_ticket(request):
    if request.method != 'POST':
        return
    serializer = TicketPurchase(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    s = serializer.data
    from_id = s['station_from']
    to_id = s['station_to']
    time_after = s['time_after']
    
    (cost, lpath) = purchase_ticket_main(from_id, to_id, time_after)

    if cost is None:
        return Response({
            "message": "no ticket available for station: %d to station:%d" % (from_id, to_id)
        }, status=status.HTTP_403_FORBIDDEN)
   
    return Response({
        'cost': cost,
        'stations': lpath
    })

    
    


@swagger_auto_schema(
    method='GET',
    query_serializer=PlanQuery, 
    responses={
        201: openapi.Schema(type= openapi.TYPE_OBJECT, properties={}),
    }
)
@api_view(['GET'])
def optimal_plan(request):
    if request.method != 'GET':
        return
    
    reqs = request.GET.dict()

    (total_cost, total_time, stations) = (0, 0, [])
    
    if len(stations) == 0:
        return Response({
            "message": "no routes available from station: %s to station: %s" % (reqs['from'], reqs['to'])
        }, status = status.HTTP_403_FORBIDDEN)
    
    custom_order = ['station_id', 'train_id', 'departure_time', 'arrival_time']

    station_data = []
    for id in stations:
        stobj = Stop.objects.get(pk = id)
        if stations[0] == id:
            stobj.arrival_time = None
        if stations[len(stations)-1] == id:
            stobj.departure_time = None

        my_dict = {field: getattr(stobj, field) for field in custom_order}
        my_dict['station_id'] = stobj.station_id_id
        my_dict['train_id'] = stobj.train_id_id
        station_data.append(my_dict)

    return Response({
        'total_cost': total_cost,
        'total_time': total_time,
        'stations': station_data
    })
