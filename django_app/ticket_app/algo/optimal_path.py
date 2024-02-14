from typing import Dict, List, Tuple
from django.db import connection

import heapq

class Edge:
    fare: int
    duration: int
    cost: int

    def __init__(
        self,
        fare: int,
        duration: int,
        cost: int
    ):
        self.fare = fare
        self.duration = duration
        self.cost = cost

        

class Node:
    value: int
    station_id: int
    dep_time: int
    edges: Dict[int, Edge]
    info: Dict[str, str]

    def __init__(
        self,
        value: int,
        station_id: int,
        dep_time: int,
        departure: str,
        arrival: str,
        train_id: int
    ):
        self.value = value
        self.station_id = station_id
        self.dep_time = dep_time
        self.edges = {}

        self.info = {
            "station_id": station_id,
            "train_id": train_id,
            "departure_time": departure,
            "arrival_time": arrival,
        }

    def add_edge(
        self,
        to,
        fare: int,
        duration: int,
        cost: int
    ):
        self.edges[to] = Edge(fare, duration, cost)
            

def dijkstra(graph: Dict[int, Node], start: int, end: int) -> Tuple[int, int, List[int]]:
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
        
        edges = graph[current_vertex].edges
        # Check all neighbors of the current vertex
        for target in edges:
            edge = edges[target]
            new_distance = current_distance + edge.cost
            if new_distance < distances[target]:
                distances[target] = new_distance
                predecessors[target] = current_vertex
                heapq.heappush(priority_queue, (new_distance, target))
    
    if end not in distances or distances[end] == float('infinity'):
        return None, None, []
    
    vertex_path = []
    current_vertex = end
    total_cost = 0
    total_time = 0

    while predecessors[current_vertex] is not None:
        vertex_path.insert(0, graph[current_vertex].info)
        prev_vertex = predecessors[current_vertex]
        edge = graph[prev_vertex].edges[current_vertex]

        total_cost += edge.fare
        total_time += edge.duration

        current_vertex = prev_vertex
    vertex_path.insert(0, graph[start].info)

    return total_time, total_cost, vertex_path
    


ENDING_NODE_VAL = 0

def time_to_minutes(time: str) -> int:
    slices = time.split(':', 3)
    return int(slices[0]) * 60 + int(slices[1])

def prepare_stops(to_id: int) -> Tuple[List[Tuple], Dict[int, Node], Dict[int, List[Node]]]:
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
    station_nodes = {}
    node_count = 0

    for stop in stops:
        (train_id, station_id, arrival_time, departure_time, fare) = stop
        dep_time = None if not bool(departure_time) else time_to_minutes(departure_time)
        arr_time = None if not bool(arrival_time) else time_to_minutes(arrival_time)
        stops2.append((train_id, station_id, fare, arr_time))

        if station_id == to_id:
            if ENDING_NODE_VAL not in graph:
                graph[ENDING_NODE_VAL] = Node(
                    ENDING_NODE_VAL,
                    station_id,
                    dep_time,
                    None,
                    arrival_time,
                    train_id
                )
            continue
        departure_time = stop[3]
        station_map = station_nodes.get(station_id)
        if station_map is None:
            station_map = []
            station_nodes[station_id] = station_map
        if not bool(departure_time):
            continue
        node_count += 1
        node = Node(
            node_count,
            station_id,
            dep_time,
            departure_time,
            arrival_time,
            train_id
        )
        station_map.append(node)
        graph[node_count] = node
    
    return stops2, graph, station_nodes


def optimal_cost_path(from_id: int, to_id: int):
    stops, graph, station_nodes = prepare_stops(to_id)
    train_last_node: Dict[int, Node] = {}

    for stop in stops:

        (train_id, station_id, fare, arr_time) = stop

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            if last_node is not None:
                last_node.add_edge(
                    ENDING_NODE_VAL,
                    fare=fare,
                    duration = arr_time - last_node.dep_time,
                    cost=fare
                )
                del train_last_node[train_id]
            continue


        station_map: List[Node] = station_nodes[station_id]
        
        for node in station_map:
            if node.info['train_id'] == train_id:
                train_last_node[train_id] = node
                if not last_node:
                    break
            if not last_node:
                continue
            last_node.add_edge(node.value, fare, node.dep_time - last_node.dep_time, fare)
                    

    if ENDING_NODE_VAL not in graph:
        return None, None, []
    
    total_time, total_cost, lpath = None, float('infinity'), []
    
    for start in station_nodes[from_id]:
        t, c, p = dijkstra(graph, start.value, ENDING_NODE_VAL)
        if c < total_cost:
            total_time, total_cost, lpath = t, c, p

    return total_time, total_cost, lpath


def optimal_time_path(from_id: int, to_id: int):
    stops, graph, station_nodes = prepare_stops(from_id, to_id)
    train_last_node: Dict[int, Node] = {}

    for stop in stops:

        (train_id, station_id, fare, arr_time) = stop

        last_node = train_last_node.get(train_id)

        if station_id == to_id:
            if last_node is not None:
                dur = arr_time - last_node.dep_time
                last_node.add_edge(
                    ENDING_NODE_VAL,
                    fare=fare,
                    duration=dur,
                    cost=dur
                )
                del train_last_node[train_id]
            continue


        station_map: List[Node] = station_nodes[station_id]
        
        for node in station_map:
            if node.info['train_id'] == train_id:
                train_last_node[train_id] = node
                if not last_node:
                    break
            if not last_node:
                continue
            dur = node.dep_time - last_node.dep_time
            last_node.add_edge(node.value, fare, dur, dur)
                    

    if ENDING_NODE_VAL not in graph:
        return None, None, []
    
    total_time, total_cost, lpath = float('infinity'), None, []
    
    for start in station_nodes[from_id]:
        t, c, p = dijkstra(graph, start.value, ENDING_NODE_VAL)
        if t < total_time:
            total_time, total_cost, lpath = t, c, p

    return total_time, total_cost, lpath

