from datetime import datetime as dt
from math import radians, cos, sin, acos, asin, sqrt
import networkx as nx

###
### TO BE OBJECTIFIED
###

def haversine(pt1, pt2):
    """
    INPUT: tuples (lon1, lat1), (lon2, lat2)
    
    OUTPUT: The great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [pt1[0], pt1[1], pt2[0], pt2[1]])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2.)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def diff_timestamps(s1, s2):
    """
    INPUT: strings of the format "HH:mm:ss"
            Per GTFS rules, HH can take values greater than 24
            (due to trips that extend past midnight)
    OUTPUT: time in seconds between s1 and s2        
    """
    if int(s1[:2]) >= 24:
        s1 = '0' + str(int(s1[:2])%24) + s1[2:]
    if int(s2[:2]) >= 24:
        s2 = '0' + str(int(s2[:2])%24) + s2[2:]
    tdelt = dt.strptime(s2, '%H:%M:%S') - dt.strptime(s1, '%H:%M:%S')
    return tdelt.seconds

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
        if (t2 > t1) and (diff_timestamps(t1, t2) < est_time):
            try:
                p_t, p = nx.bidirectional_dijkstra(G, source, n, weight='duration')
            except nx.NetworkXNoPath:
                return p_t, p

def get_closest_stop(lat, lon, stops):
    """
    INPUT: latitude, longitude, database of stops
    OUTPUT: stop_id of closest stop to lat&lon
    """
    dist = stops.apply(lambda x: haversine((x['stop_lon'],x['stop_lat']),\
                                            (lon, lat)), axis=1)
    return dist.argmin()

def get_next_stop_timepoint(stop_id, current_time, all_stop_timepoints):
    for node in all_stop_timepoints[stop_id]:
        if node[-8] > current_time:
            return node

def get_closest_shape_pt(lat, lon, shape):
    dist = shape.apply(lambda x: haversine((x['shape_pt_lon'], \
                        x['shape_pt_lat']), (lon, lat)), axis=1)
    return dist.argmin()
    
def distance_along_route(pt_1_ind, pt_2_ind, shape):
    d1 = shape.loc[pt_1_ind]['shape_dist_traveled']
    d2 = shape.loc[pt_2_ind]['shape_dist_traveled']
    return d2 - d1 
    
def distance_from_segment(pt, seg_pt_1, seg_pt_2):
    c = haversine(seg_pt_1, seg_pt_2)
    b = haversine(seg_pt_1, pt)
    a = haversine(seg_pt_2, pt)
    
    num1 = (b**2 + c**2 - a**2)
    num2 = (a**2 + c**2 - b**2)  
    
    if (num1 < 0) or (num2 < 0):
        return min(a, b)
    
    theta = acos( num1 / (2.*b*c))
    h = b * sin(theta)
    
    return h