"""
Created on Fri Apr 29 11:33:03 2016

@author: moses
"""
import pandas as pd
import utilities as ut
import cPickle as pickle
from datetime import datetime as dt

class Schedule(object):
    def __init__(self, gtfs_path):
        # Reading in static schedule data
        self.routes = pd.read_csv(gtfs_path+'routes.txt', index_col='route_id')
        self.trips = pd.read_csv(gtfs_path+'trips.txt', index_col='trip_id')
        self.shapes = pd.read_csv(gtfs_path+'shapes.txt')
        
        stops = pd.read_csv(gtfs_path+'stops.txt', index_col='stop_id')
        stop_times = pd.read_csv(gtfs_path+'stop_times.txt')
        
        # Some of these stops are named "Not a public stop" but are still in trips.
        # Luckily, in the few trips they appear in, they're only either at the
        # beginning or the end, so we can remove them now and we'll still build
        # a nice graph with the connections we expect.
        bad_stop_ids = stops[stops.stop_name == 'Not a public stop'].index.values
        stops = stops[stops.stop_name != 'Not a public stop']

        self.stop_times = stop_times[~stop_times['stop_id'].isin(bad_stop_ids)]

        
        # Oh and some stops are in stops.txt but not used in trips... let's remove 'em
        used_stops = set(stop_times['stop_id'].unique())
        
        self.stops = stops[stops.index.isin(used_stops)]
        
        # Let's make some sorted stop-timepoint lists for each stop_id to
        # make lookup faster for things
        self.all_stop_timepoints = {}
        for stopid in used_stops:
            stopid_times = stop_times[stop_times['stop_id'] == stopid]
            stop_timepoints = stopid_times.apply(\
                    lambda x: '{0}_{1}'.format(\
                    stopid, x['arrival_time']),\
                    axis=1)            
            self.all_stop_timepoints[stopid] = sorted(list(set(stop_timepoints)))
        
        self.closest_stops()
        
        
        
    def closest_stops(self, max_dist=0.2):
        """
        Make a new dictionary stop_neighbors.
        key = stop_id, 
        val = pandas Series of stop distances for stops closer than max_dist
                (indexed by stopid)
        
        Takes a while to run...
        """
        self.stop_neighbors = {}
              
        for row in self.stops.iterrows():
            stop_id = row[0]
            stop_info = row[1]  
            # calculate distance between this stop and every other stop
            dists = self.stops.apply(lambda x: ut.haversine( (x['stop_lon'], \
                                x['stop_lat']), (stop_info['stop_lon'],\
                                stop_info['stop_lat'])), axis=1)
            # only keep the stops within max_dist
            dists = dists[dists <= max_dist]
        
            # don't connect the stop to itself, duh
            dists = dists.drop(stop_id)
            
            self.stop_neighbors[stop_id] = dists
            
    def get_closest_stop(self, lat, lon):
        """
        INPUT: latitude, longitude
        OUTPUT: stop_id of closest stop to lat&lon
        """
        dist = self.stops.apply(lambda x: \
                ut.haversine((x['stop_lon'],x['stop_lat']), (lon, lat)),\
                axis=1)
        return dist.argmin()

    def get_next_stop_timepoint(self, stop_id, time_point):
        """
        INPUT: stop_id, time_point as timestamp string 'HH:MM:SS' 
        OUTPUT: next timepoint at stop_id
        """
        for node in self.all_stop_timepoints[stop_id]:
            if node[-8:] > time_point:
                return node

if __name__ == '__main__':
    sched = Schedule('../bus_project_data/google_transit/')
    with open('schedule.pkl', 'w') as f:
        pickle.dump(sched, f)