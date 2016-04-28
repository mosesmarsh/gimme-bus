import pandas as pd
import numpy as np
import networkx as nx
from utilities import haversine, diff_timestamps

# Reading in static schedule data
stops_full = pd.read_csv('data/google_transit/stops.txt', index_col='stop_id')
routes = pd.read_csv('data/google_transit/routes.txt', index_col='route_id')
trips = pd.read_csv('data/google_transit/trips.txt', index_col='trip_id')
stop_times = pd.read_csv('data/google_transit/stop_times.txt')
shapes = pd.read_csv('data/google_transit/shapes.txt')

# Some of these stops are named "Not a public stop" but are still in trips.
# Luckily, in the few trips they appear in, they're only either at the
# beginning or the end, so we can remove them now and we'll still build
# a nice graph with the connections we expect.
stops = stops_full[~stops_full.index.isin([7520, 7530, 7531, 7540])]
stop_times = stop_times[~stop_times['stop_id'].isin([7520, 7530, 7531, 7540])]

# Oh and some stops are in stops.txt but not used in trips... let's remove 'em
used_stops = set(stop_times['stop_id'].unique())
stops = stops[stops.index.isin(used_stops)]

#Directed graph
G_x = nx.DiGraph()

# RIDING GRAPH
# For each trip, for each stop, add the stop as a node
# and connect it to the previous stop in the trip
for trip_id in trips.index:
    #trip info to store in each edge for this trip
    trip_stops = stop_times[stop_times['trip_id'] == trip_id]
    trip_info = trips.loc[trip_id]
    route_id = trip_info['route_id']
    route_short_name = routes.loc['route_id']['route_short_name']
    service_id = trip_info['service_id']
    block_id = trip_info['block_id']
    shape_id = trip_info['shape_id']

    for i, row in enumerate(trip_stops.iterrows()):
        #stop info to store in each node
        stop_id = row[1]['stop_id']
        arrival_time = row[1]['arrival_time']
        stop_info = stops.loc[stop_id]
        stop_name = stop_info['stop_name']
        stop_lat = stop_info['stop_lat']
        stop_lon = stop_info['stop_lon']

        #this is a time-expanded graph, each time-point of a stop
        #is a node
        stop_node = '{0}_{1}'.format(stop_id, arrival_time)

        #add the node if it isn't already in the graph
        if not G_x.has_node(stop_node):
            G_x.add_node(stop_node, stop_id=stop_id, stop_name=stop_name,\
                         stop_lat=stop_lat, stop_lon=stop_lon, arrival_time=arrival_time)

        #adding edges, starting with the second stop in the trip
        if i == 0:
            last_stop = stop_node
            continue
        ride_time = diff_timestamps(G_x.node[last_stop]['arrival_time'],arrival_time)
        G_x.add_edge(last_stop, stop_node, trip_id=trip_id, route_id=route_id, \
                     route_short_name=route_short_name, service_id=service_id, \
                     block_id=block_id, shape_id=shape_id, type='ride', duration=ride_time)
        last_stop = stop_node

# WAITING GRAPH
# For each stop_id, connect each timepoint to the next
sorted_nodes = sorted(G_x.nodes())
for i, node in enumerate(sorted_nodes):
    if i == 0:
        last_node = node
        continue
    node_id = G_x.node[node]['stop_id']
    node_time = G_x.node[node]['arrival_time']
    last_node_id = G_x.node[last_node]['stop_id']
    last_node_time = G_x.node[last_node]['arrival_time']
    wait_time = diff_timestamps(last_node_time, node_time)
    if node_id == last_node_id:
        G_x.add_edge(last_node, node, duration=wait_time, type='wait')
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

# # Let's make some sorted stop-timepoint lists for each stop_id to
# # make lookup faster in our loop.
# all_stop_timepoints = {}
# for stopid in used_stops:
#     all_stop_timepoints[stopid] = \
#             sorted( list( set(stop_times[stop_times['stop_id'] == stopid].\
#                               apply(lambda x: '{0}_{1}'.\
#                               format(stopid, x['arrival_time']), axis=1))))

# Let's make some sorted stop-timepoint lists for each stop_id to
# make lookup faster for things
all_stop_timepoints = {}
for stopid in used_stops:
    node_names = \
        stop_times[stop_times['stop_id'] == stopid].\
            apply(lambda x: '{0}_{1}'.\
                              format(stopid, x['arrival_time']),\
                  axis=1)
    all_stop_timepoints[stopid] = sorted(list(set(node_names)))


for row in stops.iterrows():
    stop_id = row[0]
    stop_info = row[1]

    # calculate distance between this stop and every other stop
    dists = stops.apply(lambda x: haversine( (x['stop_lon'], \
                        x['stop_lat']), (stop_info['stop_lon'],\
                        stop_info['stop_lat'])), axis=1)

    # only keep the stops within 500 meters
    dists = dists[dists <= 0.5]

    # don't connect the stop to itself, duh
    dists = dists.drop(row[0])

    # convert to walking times. add 30 seconds for maybe waiting for a stoplight, sure.
    walk_times = np.ceil(1000*dists/walk_speed) + 30

    # for every closest stop, add an edge between each stop-timepoint
    # and the earliest walkable closest stop timepoint
    for close_stop in walk_times.iteritems():
        close_stop_id = close_stop[0]
        walk_time = close_stop[1]
        for node1 in all_stop_timepoints[stop_id]:
            t1 = G_x.node[node1]['arrival_time']
            for node2 in all_stop_timepoints[close_stop_id]:
                t2 = G_x.node[node2]['arrival_time']
                tdelt = diff_timestamps(t1, t2)
                if (t2 > t1) and (tdelt >= walk_time):
                    if G_x.has_edge(node1, node2):
                        break
                    G_x.add_edge(node1, node2, duration=tdelt, type='walk')
                    break


nx.write_gpickle(G_x, 'graph_x_7.gpkl')
