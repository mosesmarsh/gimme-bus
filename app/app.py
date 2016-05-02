"""
Created on Fri Apr 29 11:04:55 2016

@author: moses
"""

from flask import Flask, request
import networkx as nx
import cPickle as pickle
from code import utilities as ut
from code.schedule import Schedule
from code.routing import GraphRouter

app = Flask(__name__)

path_to_data = '../../bus_project_data/'

with open(path_to_data+'schedule.pkl') as f:
    sched = pickle.load(f)

G_wait_walk = nx.read_gpickle(path_to_graph+'graph_waiting_walking.gpkl')
G_ride_weekday = nx.read_gpickle(path_to_graph+'graph_riding_weekday.gpkl')
G_ride_saturday = nx.read_gpickle(path_to_graph+'graph_riding_saturday.gpkl')
G_ride_sunday = nx.read_gpickle(path_to_graph+'graph_riding_sunday.gpkl')

g_router = GraphRouter(G_wait_walk, G_ride_weekday, G_ride_saturday, G_ride_sunday, sched)

# home page: welcome!
@app.route('/')
def index():
    return '''
        <p>Welcome! Think about your upcoming bus trip.</p>
        <p>When you're ready, click <a href="/submit">here</a> to go to the submit page</p>
        '''


# Form page to submit origin & destination
@app.route('/submit')
def submission_page():
    return '''
        <p>Input your origin (lat, lon) and destination (lat, lon):</p>
        <form action="/predict" method='POST' >
            <input type="text" name="user_input", size=60" />
            <input type="submit" />
        </form>
        '''


# Get the best bus path!
@app.route('/predict', methods=['POST'] )
def prediction():
    text = str(request.form['user_input'])
    origin = sched.get_closest_stop(o_lat, o_lon)
    destination = sched.get_closest_stop(d_lat, d_lon)
    current_time = 
    path = ut.quickest_route()
    directions = ut.condens_path()
    return page.format(pred[0]) + '<p>{}</p>'.format(text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
