from typing import Dict, List, Tuple
from django.db import connection

import heapq


class Node:
    value: int
    station_id: int
    edges: Dict[int, int]
    info: Dict[str, str]

    def __init__(
        self,
        value: int,
        station_id: int,
        departure: str,
        arrival: str,
        train_id: int
    ):
        self.value = value
        self.station_id = station_id
        self.edges = {}

        self.info = {
            "station_id": station_id,
            "train_id": train_id,
            "departure_time": departure,
            "arrival_time": arrival,
        }

    def add_edge(
        self,
        to: int,
        cost: int
    ):
        self.edges[to] = cost

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
        
        edges = graph[current_vertex].edges
        # Check all neighbors of the current vertex
        for target in edges:
            new_distance = current_distance + edges[target]
            if new_distance < distances[target]:
                distances[target] = new_distance
                predecessors[target] = current_vertex
                heapq.heappush(priority_queue, (new_distance, target))
    
    if end not in distances or distances[end] == float('infinity'):
        return None, []

    shortest_path = []
    current_vertex = end
    while predecessors[current_vertex] is not None:
        shortest_path.insert(0, graph[current_vertex].info)
        current_vertex = predecessors[current_vertex]
    shortest_path.insert(0, graph[start].info)

    return distances[end], shortest_path


def purchase_ticket_main(from_id: int, to_id: int, time_after: str) -> Tuple[int, List]:
    stops = []
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT train_id_id, station_id_id, arrival_time, departure_time, fare
            FROM train_app_stop
            WHERE arrival_time >= %s OR departure_time >= %s
            ORDER BY stop_id ASC
            """,
            [time_after, time_after]
        )
        stops = cursor.fetchall()


    STARTING_NODE_VAL = 0
    ENDING_NODE_VAL = 1

    """
    Every unique combination of station & departing train resembles a node here.

    In this algorithm, we go to a station by a train.
    Then for each Node of this station, create a path with prev node of this train
    if departure time of the node is >= arrival of the train
    """
    graph = {}
    station_time_node = {}
    node_count = 1

    """
    We need this first loop to assign the nodes(departure) to each station first,
    for a train may appear later in the loop but has arrival time that's early
    """
    for stop in stops:
        (train_id, station_id, arrival_time, departure_time, fare) = stop

        if station_id == from_id:
            if STARTING_NODE_VAL not in graph:
                graph[STARTING_NODE_VAL] = Node(
                    STARTING_NODE_VAL,
                    station_id,
                    departure_time,
                    None,
                    train_id
                )
            continue
        if station_id == to_id:
            if ENDING_NODE_VAL not in graph:
                graph[ENDING_NODE_VAL] = Node(
                    ENDING_NODE_VAL,
                    station_id,
                    None,
                    arrival_time,
                    train_id
                )
            continue
        station_map = station_time_node.get(station_id)
        if station_map is None:
            station_map = []
            station_time_node[station_id] = station_map
        if not bool(departure_time):
            continue
        node_count += 1
        node = Node(
            node_count,
            station_id,
            departure_time,
            arrival_time,
            train_id
        )
        station_map.append(node)
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
                last_node.add_edge(
                    ENDING_NODE_VAL,
                    cost=fare
                )
                del train_last_node[train_id]
            continue

        station_map: List[Node] = station_time_node[station_id]
        
        for node in station_map:
            if node.info['train_id'] == train_id:
                train_last_node[train_id] = node
                if not last_node:
                    break
            if not last_node:
                continue
            last_node.add_edge(node.value, fare)
                
    if STARTING_NODE_VAL not in graph or ENDING_NODE_VAL not in graph:
        return None, []
    
    return dijkstra(graph, STARTING_NODE_VAL, ENDING_NODE_VAL)