from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from train_app.models import Stop
from users_app.models import *
from station_app.models import *
from typing import Dict, List, Set, Tuple

from django.db.models import Q

from queue import PriorityQueue
import datetime
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


def get_cheapest_path(
    train_stops: Dict[int, List[Stop]],
    common_stops: Dict[int, Set[int]],
    train_station_idx: Dict[str, int],
    queue: List[Tuple[int, int]],
):
    (train_id, from_id) = queue.pop()
    stops = train_stops[train_id]
    ts_idx = train_station_idx.get("%d_%d" % (train_id, from_id))

    if ts_idx is not None:
        this_station = stops[ts_idx]
        other_trains = common_stops[this_station.station_id]
        other_trains.remove(train_id)

    if len(queue) > 0:
        get_cheapest_path(train_stops, common_stops, train_station_idx, queue)
        


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
    # time_after = s['time_after']
   
    stops = Stop.objects.filter(
        Q(station_id=from_id) | Q(station_id=to_id)
    ).order_by('train_id', 'stop_id')

    edges = []
    station_time_node = {}
    node_count = 0
    train_last_node = {}


    """
    Every unique combination of station & departure time of a train resembles a node here.

    In this algorithm, we go to a station by a train. Then:
    1. Get/create a node with the departure time of this train.
    2. Add a path to all departure times that's >= this train's
    3. A path from this station to the next station will be added 
       in the next iteration as last_stop of this train will be this one
    """

    for stop in stops:
        has_arrival = bool(stop.arrival_time)
        has_departure = bool(stop.departure_time)
        last_node = train_last_node.get(stop.train_id)

        if not has_arrival and not has_departure:
            """
            This stop neither has a arrival time, nor a departure time
            Therefore we cannot switch train in this node
            """
            node_count += 1
            node = node_count
            if last_node is not None:
                edges.append((last_node, node, stop.fare))
            train_last_node[stop.train_id] = node
            continue

        station_map = station_time_node.get(stop.station_id)
        if station_map is None:
            station_map = {}
            station_time_node[stop.station_id] = station_map


        if has_departure:
            """
            This stop has a departure time, so we need to create a node
            for this departure time if it does not already exist.
            So that the traveller can switch to this train if it fits
            """
            node = station_map.get(stop.departure_time)
            if node is None:
                node_count += 1
                node = node_count
                station_map[stop.departure_time] = node
        else:
            node_count += 1
            node = node_count
            if last_node is not None:
                """
                We need to add this to edges list,
                becasue it won't get added in the station_map loop
                """
                edges.append((last_node, node, stop.fare))

        train_last_node[stop.train_id] = node
        if last_node is None:
            continue
            
            
        max_delay = stop.arrival_time if has_arrival else stop.departure_time
        for time, node in station_map:
            if time >= max_delay:
                edges.append((last_node, node, stop.fare))
        
    
    print(edges)

    # get_cheapest_path(to_id, train_routes)

    return Response({})

    
    


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
