import pandas as pd
import numpy as np
import networkx as nx
import utilities as ut
from schedule import Schedule
import cPickle as pickle

#gtfs_dir = '../bus_project_data/google_transit/'
#sched = sch.Schedule(gtfs_dir)
with open('schedule.pkl') as f:
    sched = pickle.load(f)

#Directed graph
G = nx.DiGraph()

# make a node for each stop_timepoint
nodes = []
for val in sched.all_stop_timepoints.itervalues():
        nodes.extend(val)

# write node_list
#with open('nodes.txt', 'w') as f:
#    f.write('\n'.join(nodes))

G.add_nodes_from(nodes)

# WAITING GRAPH
# For each stop_id, connect each timepoint to the next
for i, node in enumerate(nodes):
    if i == 0:
        last_node = node
        continue
    node_id = node[:-9]
    node_time = node[-8:]
    last_node_id = last_node[:-9]
    last_node_time = last_node[-8:]
    wait_time = ut.diff_timestamps(last_node_time, node_time)
    if node_id == last_node_id:
        G.add_edge(last_node, node, duration=wait_time, type='wait')
    last_node = node

# WALKING GRAPH
# Adding edges between stops that are within walking distance (200 meters)
# For every stop, find the closest stops.
# For every closest stop, add an edge between each stop-timepoint
# and the earliest walkable closest stop timepoint

#foot speeds in m/s
walk_speed = 1.39
run_speed = 4.47
sprint_speed = 6.7

for stop_id, neighbors in sched.stop_neighbors.iteritems():

    # convert to walking times. add 30 seconds for maybe waiting for a stoplight, sure.
    walk_times = np.ceil(1000.*neighbors/walk_speed) + 30

    # for every closest stop, add an edge between each stop-timepoint
    # and the earliest walkable closest stop timepoint
    for close_stop in walk_times.iteritems():
        close_stop_id = close_stop[0]
        walk_time = close_stop[1]
        for node1 in sched.all_stop_timepoints[stop_id]:
            t1 = node1[-8:]
            for node2 in sched.all_stop_timepoints[close_stop_id]:
                t2 = node1[-8:]
                tdelt = ut.diff_timestamps(t1, t2)
                if (t2 > t1) and (tdelt >= walk_time):
                    if G.has_edge(node1, node2):
                        pass
                    G.add_edge(node1, node2, duration=tdelt, type='walk')
                    break

# RIDING GRAPH
# For each trip, for each stop, add the stop as a node
# and connect it to the previous stop in the trip
G_ride_weekday = nx.DiGraph()
G_ride_saturday = nx.DiGraph()
G_ride_sunday = nx.DiGraph()
for trip_id in sched.trips.index:
    # Trip info to store in each edge for this trip
    trip_stops = sched.stop_times[sched.stop_times['trip_id'] == trip_id]
    trip_info = sched.trips.loc[trip_id]
    route_id = trip_info['route_id']
    route_short_name = sched.routes.loc['route_id']['route_short_name']
    service_id = trip_info['service_id']
    block_id = trip_info['block_id']
    shape_id = trip_info['shape_id']

    for i, row in enumerate(trip_stops.iterrows()):
        #stop info to store in each node
        stop_id = row[1]['stop_id']
        arrival_time = row[1]['arrival_time']
        stop_info = sched.stops.loc[stop_id]

        #this is a time-expanded graph, each time-point of a stop
        #is a node
        stop_node = '{0}_{1}'.format(stop_id, arrival_time)

        #adding edges, starting with the second stop in the trip
        if i == 0:
            last_stop = stop_node
            continue
        ride_time = ut.diff_timestamps(last_stop[-8:],arrival_time)
        
        edge_tuple = (last_stop, stop_node, dict(trip_id=trip_id, route_id=route_id, \
                     route_short_name=route_short_name, service_id=service_id, \
                     block_id=block_id, shape_id=shape_id, type='ride',\
                     duration=ride_time))
        if service_id == 1:
            G_ride_weekday.add_edge(edge_tuple)
        if service_id == 2:
            G_ride_saturday.add_edge(edge_tuple)
        if service_id == 3:
            G_ride_sunday.add_edge(edge_tuple)
        
        
        last_stop = stop_node


nx.write_gpickle(G, 'graph_waiting_walking.gpkl')
nx.write_gpickle(G_ride_weekday, 'graph_riding_weekday.gpkl')
nx.write_gpickle(G_ride_saturday, 'graph_riding_saturday.gpkl')
nx.write_gpickle(G_ride_sunday, 'graph_riding_sunday.gpkl')
