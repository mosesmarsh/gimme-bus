"""
Created on Mon Apr 25 10:55:15 2016

@author: moses
"""
import networkx as nx
import pandas as pd
import numpy as np
from schedule import Schedule
import utilities as ut
import cPickle as pickle


with open('schedule.pkl') as f:
    sched = pickle.load(f)
    
G = nx.read_gpickle('graph_waiting_walking.gpkl')
G_ride_weekday = nx.read_gpickle('graph_riding_weekday.gpkl')
G_ride_saturday = nx.read_gpickle('graph_riding_saturday.gpkl')
G_ride_sunday = nx.read_gpickle('graph_riding_sunday.gpkl')

def condense_path(G, path, routes):
    """
    INPUT: graph G
           path: list of stops (nodes) traversed
           routes: database of trips between stops    
    OUTPUT: path that only lists stops involving a transfer
    """
    last_step = 0
    condensed_path = []
    for i in xrange(len(path) - 1):
        # Get route_id for trip connecting nodes. If the nodes are
        # connected with a "walking" edge, set route = 'Walk'
        route = G[path[i]][path[i+1]].get('route_id', 'Walk')
        if route == last_step:
            continue
        condensed_path.append(path[i])
        last_step = route
    condensed_path.append(path[-1])
    return condensed_path

def print_path(G, p, routes, condensed=True):
    """
    INPUT: graph G, path p, route_db routes
    OUTPUT: path in human-readable directions
        e.g. "08:15:00: Arrive at Walnut & California
                        Take 44 to Water & Chestnut
    """
    path = p
    if condensed:
        path = condense_path(p)

    for i in xrange(len(path) - 1):
        route = G[path[i]][path[i+1]].get('route_id', 'Walk')
        if route != 'Walk':
            route = 'Take ' + routes.loc[route]['route_short_name']
        print '{0}: Arrive at {1}.\n\t  {2} to {3}'.\
                    format(G.node[path[i]]['arrival_time'], \
                           G.node[path[i]]['stop_name'], \
                           route, G.node[path[i+1]]['stop_name'])
    print '{0}: Arrive at {1}'.format(G.node[path[-1]]['arrival_time'],\
                                      G.node[path[-1]]['stop_name'])

def quickest_route(source, target, G, all_stop_timepoints, est_time=7200):
    """
    INPUT: source node 'stopid_timestamp' (a stop_timepoint string)
           target node stop_id
           graph of stops & trips G
           all_stop_timepoints: dict: key = stopid
                                       val = list of all timepoints for stopid
           estimated trip time in seconds
    OUTPUT: path_time (seconds), path (list of stop_timepoints)
           
    """
    t1 = source[-8:]
    p_t, p = None, None
    for n in all_stop_timepoints[target][::-1]:
        t2 = n[-8:]
        if (t2 > t1) and (ut.diff_timestamps(t1, t2) < est_time):
            try:
                p_t, p = nx.bidirectional_dijkstra(G, source, n, weight='duration')
            except nx.NetworkXNoPath:
                return p_t, p