from typing import Dict, List, Tuple
from django.db import connection

import heapq, json

class Node:
    value: int
    paths: Dict[int, int]
    station_id: int
    train_id: int
    departure_time: str
    departure_minute: int
    arrival_time: str
    arrival_minute: int

    def __init__(
        self,
        value: int,
        station_id: int,
        train_id: int,
        departure_time: str,
        departure_minute: int,
        arrival_time: str,
        arrival_minute: int,
    ) -> None:
        self.value = value
        self.paths = {}
        self.station_id = station_id
        self.train_id = train_id
        self.departure_time = departure_time
        self.departure_minute = departure_minute
        self.arrival_time = arrival_time
        self.arrival_minute = arrival_minute
        
    
    def add_path(self, to: int, weigth: int):
        oldw = self.paths.get(to)
        if oldw is None or oldw > weigth:
            self.paths[to] = weigth
            

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
    
    
    shortest_path = []
    current_vertex = end
    while predecessors[current_vertex] is not None:
        node = graph[current_vertex]
        shortest_path.insert(0, {
            'station_id': node.station_id
        })
        current_vertex = predecessors[current_vertex]
    
    node = graph[start]
    shortest_path.insert(0, {
        'station_id': node.station_id
    })
    
    if end in distances:
        return distances[end], shortest_path
    return None, []


STARTING_NODE_VAL = 0
ENDING_NODE_VAL = 1

def time_to_minutes(time: str) -> int:
    slices = time.split(':', 3)
    return int(slices[0]) * 60 + int(slices[1])

def prepare_stops(from_id: int, to_id: int) -> Tuple[List[Tuple], Dict, Dict]:
    stops = []
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT train_id_id, station_id_id, arrival_time, departure_time, fare
            FROM train_app_stop
            ORDER BY stop_id ASC
            """
        )
        stops = cursor.fetchall()

    stops2 = []

    graph = {}
    station_time_node = {}
    node_count = 1

    for stop in stops:
        print(stop)
        (train_id, station_id, arrival_time, departure_time, fare) = stop
        dep_time = None if not bool(departure_time) else time_to_minutes(departure_time)
        arr_time = None if not bool(arrival_time) else time_to_minutes(arrival_time)
        stops2.append((train_id, station_id, arrival_time, departure_time, fare, arr_time, dep_time))

        if station_id == from_id:
            print("Ok strat")
            if STARTING_NODE_VAL not in graph:
                graph[STARTING_NODE_VAL] = Node(
                    STARTING_NODE_VAL,
                    station_id=station_id,
                    train_id=train_id,
                    departure_time=departure_time,
                    departure_minute=dep_time,
                    arrival_time=arrival_time,
                    arrival_minute=arr_time
                )
            continue
        if station_id == to_id:
            print("Ok End")
            if ENDING_NODE_VAL not in graph:
                graph[ENDING_NODE_VAL] = Node(
                    ENDING_NODE_VAL,
                    station_id=station_id,
                    train_id=train_id,
                    departure_time=departure_time,
                    departure_minute=dep_time,
                    arrival_time=arrival_time,
                    arrival_minute=arr_time
                )
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
            node = Node(
                node_count,
                station_id=station_id,
                train_id=train_id,
                departure_time=departure_time,
                departure_minute=dep_time,
                arrival_time=arrival_time,
                arrival_minute=arr_time
            )
            station_map[departure_time] = node
            graph[node_count] = node
    
    return stops2, graph, station_time_node


def optimal_cost_path(from_id: int, to_id: int):
    stops, graph, station_time_node = prepare_stops(from_id, to_id)
    train_last_node = {}

    for stop in stops:

        (train_id, station_id, arrival_time, departure_time, fare, _, _) = stop

        if station_id == from_id:
            train_last_node[train_id] = graph[STARTING_NODE_VAL]
            continue
            

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            if last_node is not None:
                last_node.add_path(ENDING_NODE_VAL, fare)
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
                last_node.add_path(node.value, fare)
                    
    # print("\n\n\nGraph:\n")
    # for node_val in graph:
    #     print("%d\t%s\n" % (node_val, json.dumps(graph[node_val].paths, indent=2)))

    if STARTING_NODE_VAL not in graph or ENDING_NODE_VAL not in graph:
        return None, []
    
    return dijkstra(graph, STARTING_NODE_VAL, ENDING_NODE_VAL)


def optimal_time_path(from_id: int, to_id: int):
    stops, graph, station_time_node = prepare_stops(from_id, to_id)
    train_last_node: Dict[int, Node] = {}

    for stop in stops:

        (train_id, station_id, arrival_time, departure_time, _, arrival_minute, _) = stop
        if station_id == from_id:
            train_last_node[train_id] = graph[STARTING_NODE_VAL]
            continue
            

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            if last_node is not None:
                last_node.add_path(ENDING_NODE_VAL, arrival_minute - last_node.departure_minute)
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
                last_node.add_path(node.value, node.departure_minute - last_node.departure_minute)
                    
    # print("\n\n\nGraph:\n")
    # for node_val in graph:
    #     print("%d\t%s\n" % (node_val, json.dumps(graph[node_val].paths, indent=2)))

    if STARTING_NODE_VAL not in graph or ENDING_NODE_VAL not in graph:
        return None, []
    
    return dijkstra(graph, STARTING_NODE_VAL, ENDING_NODE_VAL)

