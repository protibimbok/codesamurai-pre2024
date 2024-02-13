from typing import Dict, List, Tuple

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
