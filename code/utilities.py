from datetime import datetime as dt
from math import radians, cos, sin, acos, asin, sqrt
import networkx as nx

###
### TO BE OBJECTIFIED
###


# First, some functions for finding distance in TIME and SPACE

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




## These functions will go in model.py for matching historical GPS
## positions to the defined route shapes

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