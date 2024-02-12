from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from train_app.models import Stop
from users_app.models import *
from station_app.models import *

from django.db import connection

import heapq


def dijkstra(edges, start):
    # Initialize distances dictionary
    distances = {vertex: float('infinity') for vertex in set(sum(([edge[0], edge[1]] for edge in edges), []))}
    distances[start] = 0
    
    # Priority queue to store vertices to visit
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)
        
        # Ignore the vertex if we have already found a shorter path to it
        if current_distance > distances[current_vertex]:
            continue
        
        # Check all neighbors of the current vertex
        for edge in edges:
            source, target, weight = edge
            # Update the distance if a shorter path is found
            if source == current_vertex:
                new_distance = current_distance + weight
                if new_distance < distances[target]:
                    distances[target] = new_distance
                    heapq.heappush(priority_queue, (new_distance, target))
    
    return distances


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

    stops = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT train_id_id, station_id_id, arrival_time, departure_time, fare FROM train_app_stop ORDER BY train_id_id ASC, stop_id ASC")
        stops = cursor.fetchall()

    edges = []
    station_time_node = {}
    node_count = 0
    train_last_node = {}
    from_to_edge_map = {}


    """
    Every unique combination of station & departure time of a train resembles a node here.

    In this algorithm, we go to a station by a train. Then:
    1. Get/create a node with the departure time of this train.
    2. Add a path to all departure times that's >= this train's
    3. A path from this station to the next station will be added 
       in the next iteration as last_stop of this train will be this one
    """


    for stop in stops:


        (train_id, station_id, arrival_time, departure_time, fare) = stop

        if not bool(departure_time):
            last_node = train_last_node.get(train_id)
            if last_node is not None:
                edges.append((last_node, 0, fare))
            continue

        station_map = station_time_node.get(station_id)
        if station_map is None:
            station_map = {}
            station_time_node[station_id] = station_map
      
        node = None
        
        node = station_map.get(departure_time)

        if node is None:
            node_count += 1
            node = node_count
            station_map[departure_time] = node
        
        
        last_node = train_last_node.get(train_id)
        train_last_node[train_id] = node

        if last_node is None:
            """
            This is the beginning of journey for this train,
            so we don't need to create a path with anything
            """
            continue
        
        
        for time in station_map:
            if time >= arrival_time:
                node = station_map[time]
                ft_kv = "%d_%d" % (last_node, node)
                edge_idx = from_to_edge_map.get(ft_kv)
                if edge_idx is None:
                    from_to_edge_map[ft_kv] = len(edges)
                    edges.append((last_node, node, fare))
                elif edges[edge_idx][2] > fare:
                    edges[edge_idx][2] = fare
    
    from_nodes = station_time_node.get(from_id)

    if from_nodes is None:
        return Response({
            'message': 'No routes found'
        }, status=status.HTTP_404_NOT_FOUND)

    lowest = float('infinity')
    for k  in from_nodes:
        from_node = from_nodes[k]
        cost = dijkstra(edges, from_node)[0]
        if cost < lowest:
            lowest = cost

    return Response({
        'cost': lowest
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
