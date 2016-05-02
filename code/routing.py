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
from time import time
import datetime as dt

class GraphRouter(object):
    
    def __init__(self, G_wait_walk, G_ride_week, G_ride_sat, G_ride_sun, sched):
        self.G = G_wait_walk
        self.G_ride_week = G_ride_week
        self.G_ride_sat = G_ride_sat
        self.G_ride_sun = G_ride_sun

        self.schedule = sched
        today_number = dt.date.today().weekday()
        if today_number <= 4:
            self.G.add_edges_from(self.G_ride_week)
        if today_number == 5:
            self.G.add_edges_from(self.G_ride_sat)            
        if today_number == 6:
            self.G.add_edges_from(self.G_ride_sun)
            
    def quickest_route(self, source, target, est_time=7200):
        """
        INPUT: source node 'stopid_timestamp' (a stop_timepoint string)
               target node stop_id
               estimated trip time in seconds
        OUTPUT: path_time (seconds), path (list of stop_timepoints)
               
        """
        t1 = source[-8:]
        p_t, p = None, None
        for n in self.schedule.all_stop_timepoints[target][::-1]:
            t2 = n[-8:]
            if (t2 > t1) and (ut.diff_timestamps(t1, t2) < est_time):
                try:
                    p_t, p = nx.bidirectional_dijkstra(self.G, source, n, weight='duration')
                except nx.NetworkXNoPath:
                    return p_t, p


    def condense_path(self, path):
        """
        INPUT: path: list of stops (nodes) traversed
        OUTPUT: path that only lists stops involving a transfer
        """
        last_step = 0
        condensed_path = []
        for i in xrange(len(path) - 1):
            # Get route_id for trip connecting nodes. If the nodes are
            # connected with a "walking" edge, set route = 'Walk'
            route = self.G[path[i]][path[i+1]].get('route_id', 'Walk')
            if route == last_step:
                continue
            condensed_path.append(path[i])
            last_step = route
        condensed_path.append(path[-1])
        return condensed_path
    
    def print_path(self, path, condensed=True):
        """
        INPUT: graph G, path p, route_db routes
        OUTPUT: path in human-readable directions
            e.g. "08:15:00: Arrive at Walnut & California
                            Take 44 to Water & Chestnut
        """
        if condensed:
            path = self.condense_path(path)
    
        for i in xrange(len(path) - 1):
            route = self.G[path[i]][path[i+1]].get('route_id', 'Walk')
            if route != 'Walk':
                route = 'Take ' + self.schedule.routes.loc[route]['route_short_name']
            print '{0}: Arrive at {1}.\n\t  {2} to {3}'.\
                        format(self.G.node[path[i]]['arrival_time'], \
                               self.G.node[path[i]]['stop_name'], \
                               route, self.G.node[path[i+1]]['stop_name'])
        print '{0}: Arrive at {1}'.format(self.G.node[path[-1]]['arrival_time'],\
                                          self.G.node[path[-1]]['stop_name'])
    
if __name__ == '__main__':
    with open('schedule.pkl') as f:
        sched = pickle.load(f)
    
    G_wait_walk = nx.read_gpickle('graph_waiting_walking.gpkl')
    G_ride_weekday = nx.read_gpickle('graph_riding_weekday.gpkl')
    G_ride_saturday = nx.read_gpickle('graph_riding_saturday.gpkl')
    G_ride_sunday = nx.read_gpickle('graph_riding_sunday.gpkl')
    
    g_router = GraphRouter(G_wait_walk, G_ride_weekday, G_ride_saturday, G_ride_sunday, sched)