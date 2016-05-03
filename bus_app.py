"""
Created on Fri Apr 29 11:04:55 2016

@author: moses
"""

from flask import Flask, request, render_template
import networkx as nx
import cPickle as pickle
from datetime import datetime as dt
from gimmebus import utilities as ut
from gimmebus.schedule import Schedule
from gimmebus.routing import GraphRouter

app = Flask(__name__)

# home page: welcome!
@app.route('/')
def index():
    return render_template('index.html')


# Get the best bus path!
@app.route('/route', methods=['POST'] )
def prediction():
    text = str(request.form['user_input'])
    
    # get the closest stops to the origin and destination
    loc = [float(x) for x in text.split(',')]    
    origin_id = sched.get_closest_stop(loc[0], loc[1])   
    current_timestamp = '09:33:00' #dt.strftime(dt.now(), '%H:%M:%S')
    origin = sched.get_next_stop_timepoint(origin_id, current_timestamp)
    destination_id = sched.get_closest_stop(loc[2], loc[3])
    
    # get the path
    path_time, path = g_router.quickest_route(origin, destination_id)
    directions = g_router.path_directions(path)
    return render_template('results.html', directions=directions)


if __name__ == '__main__':

    data_dir = '../bus_project_data/'

    with open(data_dir + 'schedule.pkl') as f:
        sched = pickle.load(f)

    G_wait_walk = nx.read_gpickle(data_dir + 'graph_waiting_walking.gpkl')
    G_ride_weekday = nx.read_gpickle(data_dir + 'graph_riding_weekday.gpkl')
    G_ride_saturday = nx.read_gpickle(data_dir + 'graph_riding_saturday.gpkl')
    G_ride_sunday = nx.read_gpickle(data_dir + 'graph_riding_sunday.gpkl')

    g_router = GraphRouter(G_wait_walk, G_ride_weekday, \
                            G_ride_saturday, G_ride_sunday, sched)

    app.run(host='0.0.0.0', port=8080, debug=False)
