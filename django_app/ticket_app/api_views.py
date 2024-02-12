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
from django.test import TestCase
from train_app.models import *
from users_app.models import *
from station_app.models import *
# Create your tests here.
from queue import PriorityQueue
from django.db.models import Q
import datetime


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(":"))
    total_minutes = hours * 60 + minutes
    return total_minutes


def dijkstra_for_cheapest_route(station_from, station_to, timeafter):
    # Initialize distances to all nodes as infinity except the start node
    station_to = int(station_to)
    station_from = int(station_from)
        
    totaltime = 0
    totalcost = 0
    path = []

    costs = {}
    times = {}

    stations = Station.objects.all()
    for station in stations:
        costs[station.station_id] = 10000000000000000000
        times[station.station_id] = "99:99"

    costs[station_from] = 0
    times[station_from] = timeafter

    pq = PriorityQueue()
    pq.put((costs[station_from], times[station_from], station_from, -1))
    
    pqpath = []

    while not pq.empty():
        # Pop the node with the smallest distance from the priority queue
        current_fare, arr_time, current_station, pathind = pq.get()
                
        #print(current_station)
        #print(station_to)
        if current_station == station_to:
            totalcost = current_fare
            endstop = Stop.objects.get(stop_id = pqpath[pathind][1])
            endstop = Stop.objects.filter(train_id = endstop.train_id.train_id, 
                                        arrival_time__gte = endstop.departure_time).order_by('arrival_time').first()
            path.append(endstop.stop_id)
            path.append(pqpath[pathind][1])
            while pqpath[pathind][0] != -1:
                pathind = pqpath[pathind][0]
                path.append(pqpath[pathind][1])
            #path.append(station_from)
            path.reverse()

            totaltime = time_to_minutes(times[station_to]) - time_to_minutes(Stop.objects.get(stop_id=path[0]).departure_time)
            break
        
        train_stops = Stop.objects.filter(station_id = current_station).filter(~Q(departure_time = None), departure_time__gte = arr_time)
        
        print(train_stops)
        for train_stop in train_stops:
                
            #print(train_stop)
            to_stop = Stop.objects.filter(train_id = train_stop.train_id.train_id, 
                                          arrival_time__gte = train_stop.departure_time).order_by('arrival_time').first()
            
            if to_stop != None and costs[to_stop.station_id.station_id] > current_fare + to_stop.fare:
                print(to_stop)
                costs[to_stop.station_id.station_id] = current_fare + to_stop.fare
                times[to_stop.station_id.station_id] = to_stop.arrival_time

                pq.put((costs[to_stop.station_id.station_id], times[to_stop.station_id.station_id], to_stop.station_id.station_id, len(pqpath)))
                pqpath.append((pathind, train_stop.stop_id))

    print(path)
    return (totalcost, totaltime, path)



def dijkstra_for_shortesttime_route(station_from, station_to, timeafter):
    # Initialize distances to all nodes as infinity except the start node
    station_to = int(station_to)
    station_from = int(station_from)
        
    totaltime = 0
    totalcost = 0
    path = []

    costs = {}
    times = {}

    stations = Station.objects.all()
    for station in stations:
        costs[station.station_id] = 10000000000000000000
        times[station.station_id] = 10000000000000000000

    costs[station_from] = 0
    times[station_from] = 0

    pq = PriorityQueue()
    pq.put((times[station_from], costs[station_from], timeafter, station_from, -1))
    
    pqpath = []

    while not pq.empty():
        # Pop the node with the smallest distance from the priority queue
        current_time, current_fare, arr_time, current_station, pathind = pq.get()
                
        #print(current_station)
        #print(station_to)
        if current_station == station_to:
            totalcost = current_fare
            
            endstop = Stop.objects.get(stop_id = pqpath[pathind][1])
            endstop = Stop.objects.filter(train_id = endstop.train_id.train_id, 
                                        arrival_time__gte = endstop.departure_time).order_by('arrival_time').first()
            path.append(endstop.stop_id)
            path.append(pqpath[pathind][1])
            while pqpath[pathind][0] != -1:
                pathind = pqpath[pathind][0]
                path.append(pqpath[pathind][1])
            #path.append(station_from)
            path.reverse()

            totaltime = times[station_to]
            break

        train_stops = Stop.objects.filter(station_id = current_station).filter(~Q(departure_time = None), departure_time__gte = arr_time)

        print(train_stops)
        for train_stop in train_stops:
            to_stop = Stop.objects.filter(train_id = train_stop.train_id.train_id, 
                                          arrival_time__gte = train_stop.departure_time).order_by('arrival_time').first()
            
            to_stop_arr_time = current_time + time_to_minutes(to_stop.arrival_time)
            if pathind == -1:
                to_stop_arr_time -= time_to_minutes(train_stop.departure_time)
            else :
                to_stop_arr_time -= time_to_minutes(arr_time)
            print(to_stop_arr_time)
            if to_stop != None and times[to_stop.station_id.station_id] > to_stop_arr_time:
                print(to_stop)
                costs[to_stop.station_id.station_id] = current_fare + to_stop.fare
                times[to_stop.station_id.station_id] = to_stop_arr_time

                pq.put((times[to_stop.station_id.station_id], costs[to_stop.station_id.station_id], to_stop.arrival_time, to_stop.station_id.station_id, len(pqpath)))
                pqpath.append((pathind, train_stop.stop_id))

    print(path)
    return (totalcost, totaltime, path)


def plan_optimal_route(station_from, station_to, order_by, timeafter):

    if timeafter != None :
        return dijkstra_for_cheapest_route(station_from, station_to, timeafter)
    elif order_by == "cost":
        return dijkstra_for_cheapest_route(station_from, station_to, "00:00")
    else:
        return dijkstra_for_shortesttime_route(station_from, station_to, "00:00")




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
    
    (total_cost, total_time, stations) = plan_optimal_route(serializer.station_from, serializer.station_to, "cost", serializer.time_after)

    
    


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

    (total_cost, total_time, stations) = plan_optimal_route(reqs['from'], reqs['to'], reqs['optimize'], None)
    
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
