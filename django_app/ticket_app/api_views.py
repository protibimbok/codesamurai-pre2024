from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import Ticket
from users_app.models import *
from station_app.models import *
from .algo.purchase_ticket import purchase_ticket_main
from .algo.optimal_path import optimal_cost_path, optimal_time_path


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
    
    from_id = serializer.validated_data['station_from']
    to_id = serializer.validated_data['station_to']
    time_after = serializer.validated_data['time_after']
    wallet_id =  serializer.validated_data['wallet_id']
    
    (cost, lpath) = purchase_ticket_main(from_id, to_id, time_after)

    if cost is None:
        return Response({
            "message": "no ticket available for station: %d to station:%d" % (from_id, to_id)
        }, status=status.HTTP_403_FORBIDDEN)
   

    wallet = User.objects.filter(pk = wallet_id).first()

    if wallet is None:
        # No need to handle
        return
    
    if wallet.balance < cost:
        return Response({
            "message": "recharge amount: %d to purchase the ticket" % (cost - wallet.balance)
        }, status=status.HTTP_402_PAYMENT_REQUIRED)
    


    
    ticket = Ticket.objects.create(
        wallet_id = wallet,
        station_from = Station(station_id = from_id),
        station_to = Station(station_id = to_id),
        time_after = time_after
    )
    wallet.balance -= cost
    wallet.save()

    return Response({
        'ticket_id': ticket.pk,
        'wallet_id': wallet.pk,
        'balance': wallet.balance,
        'stations': lpath
    }, status=status.HTTP_201_CREATED)

    
    


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

    from_id = int(reqs.get('from', 0))
    to_id = int(reqs.get('to', 0))
    optimize = reqs.get('optimize')

    (total_cost, total_time, stations) = (0, 0, [])
    
    if optimize is not None and optimize == 'cost':
        total_cost, lpath = optimal_cost_path(from_id, to_id)
    else:
        total_time, lpath = optimal_time_path(from_id, to_id)

    return Response({
        'total_cost': total_cost,
        'total_time': total_time,
        'stations': lpath
    })
