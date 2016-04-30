"""
Created on Fri Apr 29 11:04:55 2016

@author: moses
"""

from flask import Flask, request
import networkx as nx
from code import utilities as ut

app = Flask(__name__)

path_to_graph = '../../bus_project_data/graph_x_7.gpkl'
path_to_data = '../../bus_project_data/google_transit/'

G_x = nx.read_gpickle(path_to_graph)


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
    origin = ut.get_closest_stop()
    destination = ut.get_closest_stop()
    current_time = 
    path = ut.quickest_route()
    directions = ut.condens_path()
    return page.format(pred[0]) + '<p>{}</p>'.format(text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
