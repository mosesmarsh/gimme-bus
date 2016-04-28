import pandas as pd
import numpy as np
import networkx as nx
import requests
from bs4 import BeautifulSoup
import cPickle as pickle
from model.utilities import haversine

with open('model/graph.pkl') as f:
    G = pickle.load(f)

stops = pd.read_csv('data/google_transit/stops.txt')


def closest_stop(lat, lon, stop_data=stops):
    pass

def best_routes(t, o_lat, o_lon, d_lat, d_lon, G):
    ''' INPUT: departure time, origin (lat, lon), destination (lat, lon),
                G: graph of stops & routes
        OUTPUT: list of route plans & travel times
            route plan: "wait at STOP_0 for ROUTE_0 until DEPARTURE_TIME_0"
                        "de-bus at STOP_1 at ARRIVAL_TIME_1"
                        ("walk to STOP_2" if necessary)
                        "wait at STOP_1 for ROUTE_1 until DEPARTURE_TIME_1"
                        ...
                        "de-bus at STOP_N at ARRIVAL_TIME_N. You are at your
                        destination"

    '''

    origin_stop = closest_stop(o_lat, o_lon)
    destination_stop = closest_stop(d_lat, d_lon)

    path = nx.shortest_path(G, origin_stop, destination_stop)
