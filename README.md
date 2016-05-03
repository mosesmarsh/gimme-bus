# Gimme That Bus!
##### SFMuni arrival time predictions & on-the-fly transfer recommendations


### How to use this code:
- Download your transit agency's schedule in GTFS format
  - e.g. [SF MTA Schedule]
- run `schedule.py`
  - This pickles the static schedule in an easy-to-reference format
- run `build_static_graph.py`
  - This makes a time-expanded directed graph: every time point of every stop is a node, and edges represent ways to travel between nodes (waiting, walking, and riding)
- run `bus_app.py`, point your browser to http://localhost:8080/, input your origin and destination locations (as lat & lon pairs), and enjoy your bus ride!
- if you have access to historical GPS bus data (woo SFMTA: ftp://avl-data.sfmta.com/AVL_DATA/ ), you can try fitting a model using `model.py` (coming soon) for better predictions

Screenshots of the web app:<br>
![alt text](https://github.com/mosesmarsh/gimme-bus/blob/master/static/screenshot1.png "App screenshot 1")


![alt text](https://github.com/mosesmarsh/gimme-bus/blob/master/static/screenshot2.png "App screenshot 2")

Buses! In SF, they're only on time 60% of the time [[1]], making the official schedule a poor predictor of how long you'll have to wait for your bus. [NextBus] is a service that provides GPS tracking for an entire fleet of buses, and it uses this real-time location data (along with a proprietary algorithm) to make better predictions of bus arrival times. How much better? 70% accuracy [[2]].

Can we do better still? With access to the past three years of GPS bus data as well as ancillary weather data, let's try.

Snippet of data:
```
REV,REPORT_TIME,VEHICLE_TAG,LONGITUDE,LATITUDE,SPEED,HEADING,TRAIN_ASSIGNMENT,PREDICTABLE

1485,01/01/2015 16:10:59,02,-122.41961,37.80203,0.833,350.0,5904,0

1485,01/01/2015 16:11:14,02,-122.4197,37.80245,3.889,350.0,5904,0

1485,01/01/2015 16:12:12,02,-122.42003,37.80416,3.333,350.0,5904,0

1485,01/01/2015 16:12:29,02,-122.42016,37.80478,2.5,351.0,5904,0
```

Plan of attack:
- For each route, use the historical travel time between each pair of sequential stops to build a model that predicts travel time based on time of day, day of week, day of month, day of year, weather conditions, etc.
- Incorporate real-time bus progress to predict lateness.



#### Sources:

Real-time bus GPS data <br>
http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

[SF MTA schedule]: https://www.sfmta.com/about-sfmta/reports/gtfs-transit-data

CartoDB for route visualizations <br>
https://cartodb.com/


[1]: https://www.sfmta.com/about-sfmta/reports/performance-metrics/percentage-time-performance

[NextBus]: http://nextbus.cubic.com/About/How-NextBus-Works

[2]: https://goswift.ly/blog/2015/12/23/san-francisco-transit-prediction-accuracy-how-swyft-helps-you-commute-smarter-1

Sun et al, 2007, “Predicting Bus Arrival Time on the Basis of Global Positioning System Data” <br>
https://www.researchgate.net/publication/245562763_Predicting_Bus_Arrival_Time_on_the_Basis_of_Global_Positioning_System_Data

Shalaby, Farhan, 2004, “Prediction Model of Bus Arrival and Departure Times Using AVL and APC Data” <br>
http://www.nctr.usf.edu/wp-content/uploads/2010/03/JPT-7-1-Shalaby.pdf

Kidwell, 2001, “Predicting Transit Vehicle Arrival Times” <br>
http://www.glump.net/content/bus_predict/predicting_transit_vehicle_arrivals.htm

Baker, Nied, 2013, “Predicting Bus Arrivals Using One Bus Away Real-Time Data” <br>
http://homes.cs.washington.edu/~anied/papers/AConradNied_OneBusAway_Writeup_20131209.pdf

Transit Effectiveness Project (TEP) Passenger Data <br>
http://archives.sfmta.com/cms/rtep/tepdataindx.htm

Information about upcoming SF Muni route changes <br>
https://www.sfmta.com/projects-planning/projects/muni-forward-0
