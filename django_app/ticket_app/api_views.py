from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from train_app.models import Stop
from users_app.models import *
from station_app.models import *
# Create your tests here.
from queue import PriorityQueue
import datetime

def dijkstra_for_cheapest_route(station_from, station_to):
    # Initialize distances to all nodes as infinity except the start node
    init_stops = Stop.objects.filter(station_id = station_from)
    print(init_stops)

    totaltime = 0
    totalcost = 0
    path = []

    if init_stops.count == 0:
        return 
    
    costs = {}
    times = {}
    stations = Station.objects.all()
    for station in stations:
        costs[station.station_id] = 10000000000000000000
    costs[station_from] = 0
    times[station_from] = init_stops.order_by('arrival_time').first().arrival_time
    pqpath = []
    
    pq = PriorityQueue()
    for stop in init_stops:
        pq.put((stop.fare, stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
        pqpath.append((-1, stop.id))

    while not pq.empty():
        # Pop the node with the smallest distance from the priority queue
        current_fare, current_station, current_train, dep_time, ind = pq.get()
        
        # If current distance is greater than the calculated distance, ignore
        if current_fare > costs[current_station]:
            continue
        
        if current_station == station_to:
            totalcost = current_fare
            totaltime = times[station_to] - times[station_from]
            path.append(station_to)
            while pqpath[ind][0] != -1:
                ind = pqpath[ind][0]
                path.append(pqpath[ind][1])
            path.append(station_from)
            path.reverse()
            break

        train_stop = Stop.objects.filter(train_id = current_train, arrival_time__gte = dep_time).order_by('arrival_time').first()
        
        if costs[train_stop.station_id.id] > current_fare + train_stop.fare:

            costs[train_stop.station_id.id] = current_fare + train_stop.fare
            times[train_stop.station_id.id] = train_stop.arrival_time

            stops = Stop.objects.filter(station_id = train_stop.station_id.id, departure_time__gte = train_stop.arrival_time)
            for stop in stops:
                pq.put((costs[train_stop.station_id.id], stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
                pqpath.append((ind, train_stop.id))
    

    return (totalcost, totaltime, path)



def dijkstra_for_shortesttime_route(station_from, station_to):


    # Initialize distances to all nodes as infinity except the start node
    init_stops = Stop.objects.filter(station_id = station_from)
    print(init_stops)

    totaltime = 0
    totalcost = 0
    path = []

    if init_stops.count == 0:
        return 
    
    costs = {}
    times = {}
    stations = Station.objects.all()
    for station in stations:
        times[station.station_id] = datetime.datetime(2200, 12, 1, 23, 59, 59, 999999)

    costs[station_from] = 0
    times[station_from] = init_stops.order_by('arrival_time').first().arrival_time
    pqpath = []
    
    pq = PriorityQueue()
    for stop in init_stops:
        pq.put((stop.arrival_time, stop.fare, stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
        pqpath.append((-1, stop.id))

    while not pq.empty():
        # Pop the node with the smallest distance from the priority queue
        arrival_time, current_fare, current_station, current_train, dep_time, ind = pq.get()
        
        # If current distance is greater than the calculated distance, ignore
        if arrival_time > times[current_station]:
            continue
        
        if current_station == station_to:
            totalcost = current_fare
            totaltime = times[station_to] - times[station_from]
            path.append(station_to)
            while pqpath[ind][0] != -1:
                ind = pqpath[ind][0]
                path.append(pqpath[ind][1])
            path.append(station_from)
            path.reverse()
            break

        train_stop = Stop.objects.filter(train_id = current_train, arrival_time__gte = dep_time).order_by('arrival_time').first()
        
        if times[train_stop.station_id.id] > train_stop.arrival_time:

            costs[train_stop.station_id.id] = current_fare + train_stop.fare
            times[train_stop.station_id.id] = train_stop.arrival_time

            stops = Stop.objects.filter(station_id = train_stop.station_id.id, departure_time__gte = train_stop.arrival_time)
            for stop in stops:
                pq.put((train_stop.arrival_time, costs[train_stop.station_id.id], stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
                pqpath.append((ind, train_stop.id))
    

    return (totalcost, totaltime, path)

def plan_optimal_route(station_from, station_to, order_by):

    if order_by == "cost":
        return dijkstra_for_cheapest_route(station_from, station_to)
    else:
        return dijkstra_for_shortesttime_route(station_from, station_to)





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
    all_stops = Stop.objects.all()

    


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
    (total_cost, total_time, stations) = plan_optimal_route(reqs['from'], reqs['to'], reqs['optimize'])
    if len(stations) == 0:
        return Response({
            "message": "no routes available from station: %d to station: %d" % (reqs['from'], reqs['to'])
        }, status = status.HTTP_403_FORBIDDEN)
    station_data = []
    for id in stations:
        stobj = Stop.objects.get(pk = id)
        station_data.append(model_to_dict(stobj, fields=['train_id', 'station_id', 'arrival_time', 'departure_time']))
    return Response({
        'total_cost': total_cost,
        'total_time': total_time,
        'stations': station_data
    })
