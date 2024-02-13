from typing import Dict, List, Tuple
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

class Node:
    value: int
    paths: Dict[int, int]
    info: Dict[str, str]

    def __init__(self, value: int, stop: Tuple) -> None:
        self.value = value
        self.paths = {}
        self.info = {
            "station_id": stop[1],
            "train_id": stop[0],
            "departure_time": stop[3],
            "arrival_time": stop[2],
        }
    
    def add_path(self, to: int, weigth: int, stop: Tuple):
        oldw = self.paths.get(to)
        if oldw is None or oldw > weigth:
            self.paths[to] = weigth
            self.info["train_id"] = stop[0]
            self.info["arrival_time"] = stop[2]

def dijkstra(graph: Dict[int, Node], start: int, end: int) -> Tuple[int, List[int]]:
    # Initialize distances dictionary and predecessors dictionary
    distances = {vertex: float('infinity') for vertex in graph}
    predecessors = {vertex: None for vertex in graph}
    distances[start] = 0
    
    # Priority queue to store vertices to visit
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)
        
        # Ignore the vertex if we have already found a shorter path to it
        if current_distance > distances[current_vertex]:
            continue
        
        edges = graph[current_vertex].paths
        # Check all neighbors of the current vertex
        for target in edges:
            weight = edges[target]
            new_distance = current_distance + weight
            if new_distance < distances[target]:
                distances[target] = new_distance
                predecessors[target] = current_vertex
                heapq.heappush(priority_queue, (new_distance, target))
    
    # Reconstruct the shortest path
    shortest_path = []
    current_vertex = end
    while predecessors[current_vertex] is not None:
        shortest_path.insert(0, graph[current_vertex].info)
        current_vertex = predecessors[current_vertex]
    graph[start].info["arrival_time"] = None
    shortest_path.insert(0, graph[start].info)
    
    print(shortest_path)
    if end in distances:
        return distances[end], shortest_path
    return None, []


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
        cursor.execute("SELECT train_id_id, station_id_id, arrival_time, departure_time, fare FROM train_app_stop")
        stops = cursor.fetchall()


    STARTING_NODE_VAL = 0
    ENDING_NODE_VAL = 1

    """
    Every unique combination of station & departure time of a train resembles a node here.

    In this algorithm, we go to a station by a train. Then:
    1. Get/create a node with the departure time of this train.
    2. Add a path to all departure times that's >= this train's
    3. A path from this station to the next station will be added 
       in the next iteration as last_stop of this train will be this one
    """
    graph = {}
    station_time_node = {}
    node_count = 1

    """
    We need this first loop to assign the nodes(departure) to each station first,
    for a train may appear later in the loop but has arrival time that's early
    """
    for stop in stops:
        station_id = stop[1]
        if station_id == from_id:
            if STARTING_NODE_VAL not in graph:
                graph[STARTING_NODE_VAL] = Node(STARTING_NODE_VAL, stop)
            continue
        if station_id == to_id:
            if ENDING_NODE_VAL not in graph:
                graph[ENDING_NODE_VAL] = Node(ENDING_NODE_VAL, stop)
            continue
        departure_time = stop[3]
        station_map = station_time_node.get(station_id)
        if station_map is None:
            station_map = {}
            station_time_node[station_id] = station_map
        if not bool(departure_time):
            continue
        node = station_map.get(departure_time)
        if node is None:
            node_count += 1
            node = Node(node_count, stop)
            station_map[departure_time] = node
            graph[node_count] = node
        

    train_last_node = {}

    for stop in stops:


        (train_id, station_id, arrival_time, departure_time, fare) = stop

        if station_id == from_id:
            train_last_node[train_id] = graph[STARTING_NODE_VAL]
            continue
            

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            if last_node is not None:
                last_node.add_path(ENDING_NODE_VAL, fare, stop)
                del train_last_node[train_id]
            continue


        station_map = station_time_node[station_id]
        if bool(departure_time):
            node = station_map[departure_time]
            train_last_node[train_id] = node


        
        if last_node is None:
            continue
        
        
        for time in station_map:
            if time >= arrival_time:
                node: Node = station_map[time]
                last_node.add_path(node.value, fare, stop)
                    

    # print("\n\n\nGraph:\n")
    # for node_val in graph:
    #     print("%d\t%s\n" % (node_val, json.dumps(graph[node_val].paths, indent=2)))
                
    (cost, lpath) = dijkstra(graph, STARTING_NODE_VAL, ENDING_NODE_VAL)

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
