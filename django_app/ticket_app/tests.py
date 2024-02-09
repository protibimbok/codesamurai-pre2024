from django.test import TestCase
from train_app.models import *
from users_app.models import *
from station_app.models import *
# Create your tests here.
from queue import PriorityQueue
import datetime

def dijkstra_for_cheapest_route(station_from, station_to):
    # Initialize distances to all nodes as infinity except the start node
    init_stops = Stop.objects.filter(station_id_pk = station_from)
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
        costs[station.id] = 10000000000000000000
    costs[station_from] = 0
    times[station_from] = init_stops.order_by('arrival_time').first().arrival_time
    pqpath = []
    
    pq = PriorityQueue()
    for stop in init_stops:
        pq.put((stop.fare, stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
        pqpath.append((-1, stop.station_id.id))

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

        train_stop = Stop.objects.filter(train_id_pk = current_train, arrival_time__gte = dep_time).order_by('arrival_time').first()
        
        if costs[train_stop.station_id.id] > current_fare + train_stop.fare:

            costs[train_stop.station_id.id] = current_fare + train_stop.fare
            times[train_stop.station_id.id] = train_stop.arrival_time

            stops = Stop.objects.filter(station_id_pk = train_stop.station_id.id, departure_time__gte = train_stop.arrival_time)
            for stop in stops:
                pq.put((costs[train_stop.station_id.id], stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
                pqpath.append((ind, train_stop.station_id.id))
    

    return (totalcost, totaltime, path)



def dijkstra_for_shortesttime_route(station_from, station_to):


    # Initialize distances to all nodes as infinity except the start node
    init_stops = Stop.objects.filter(station_id_pk = station_from)
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
        times[station.id] = datetime.datetime(2200, 12, 1, 23, 59, 59, 999999)

    costs[station_from] = 0
    times[station_from] = init_stops.order_by('arrival_time').first().arrival_time
    pqpath = []
    
    pq = PriorityQueue()
    for stop in init_stops:
        pq.put((stop.arrival_time, stop.fare, stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
        pqpath.append((-1, stop.station_id.id))

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

        train_stop = Stop.objects.filter(train_id_pk = current_train, arrival_time__gte = dep_time).order_by('arrival_time').first()
        
        if times[train_stop.station_id.id] > train_stop.arrival_time:

            costs[train_stop.station_id.id] = current_fare + train_stop.fare
            times[train_stop.station_id.id] = train_stop.arrival_time

            stops = Stop.objects.filter(station_id_pk = train_stop.station_id.id, departure_time__gte = train_stop.arrival_time)
            for stop in stops:
                pq.put((train_stop.arrival_time, costs[train_stop.station_id.id], stop.station_id.id, stop.train_id.id, stop.departure_time, len(pqpath)))
                pqpath.append((ind, train_stop.station_id.id))
    

    return (totalcost, totaltime, path)


def plan_optimal_route(station_from, station_to, order_by):

    if order_by == "cost":
        (total_cost, total_time, stations) = dijkstra_for_cheapest_route(station_from, station_to)
    else:
        (total_cost, total_time, stations) = dijkstra_for_shortesttime_route(station_from, station_to)



