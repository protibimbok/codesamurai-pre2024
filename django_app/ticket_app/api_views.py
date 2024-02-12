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


def dijkstra(edges, start, end):
    graph = {}
    for frm, to, cost in edges:
        if frm not in graph:
            graph[frm] = []
        if to not in graph:
            graph[to] = []
        graph[frm].append((to, cost))
        graph[to].append((frm, cost))  # Assuming undirected graph

    pq = [(0, start, [])]
    visited = set()

    while pq:
        (cost, node, path) = heapq.heappop(pq)

        if node not in visited:
            visited.add(node)
            path = path + [node]

            if node == end:
                return cost, path

            for neighbor, c in graph[node]:
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + c, neighbor, path))

    return float('inf'), None


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
    node_station_map = {}


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

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            node_station_map[0] = stop
            if last_node is not None:
                edges.append((last_node, 0, fare))
                del train_last_node[train_id]
                continue

        station_map = station_time_node.get(station_id)

        if station_map is None:
            station_map = {}
            station_time_node[station_id] = station_map
      
        if bool(departure_time):
            node = station_map.get(departure_time)
            if node is None:
                node_count += 1
                node = node_count
                node_station_map[node] = stop
                station_map[departure_time] = node
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
    lpath = []
    for k  in from_nodes:
        from_node = from_nodes[k]
        cost, node_seq = dijkstra(edges, from_node, 0)
        if cost < lowest:
            lowest = cost
            lpath = node_seq
    
    lpath_d = []
    for node in lpath:
        (train_id, station_id, arrival_time, departure_time, fare) = node_station_map[node]
        lpath_d.append({
            'station_id': station_id,
            'train_id': train_id,
            'departure_time': departure_time,
            'arrival_time': arrival_time
        })

    return Response({
        'cost': lowest,
        'stations': lpath_d
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
