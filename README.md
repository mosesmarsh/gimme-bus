# Gimme That Bus!
##### SFMuni arrival time predictions & on-the-fly transfer recommendations

Buses! In SF, they're only on time 60% of the time [[1]], making the official schedule a poor predictor of how long you'll have to wait for your bus. [NextBus] is a service that provides GPS tracking for an entire fleet of buses, and it uses this real-time location data (along with a proprietary algorithm) to make better predictions of bus arrival times. How much better? 70% accuracy.

Goal #1: I would like to beat this number. With access to the past three years of GPS bus data as well as ancillary weather data, I will attempt to build a better predictive model.

Goal #2: Build an app that recommends bus transfers on the fly. Given a rider's current location (possibly already on a bus) and their destination, this app would use real-time location and prediction data to calculate the fastest series of buses to take. This would involve looking at all the relevant routes and route-crossings, finding the best path, then evaluating the feasibility of making the transfer given the real-time data. Hopefully this outperforms the usual strategy of looking up the route before the trip and using the official timed transfer points.

Snippet of data:
```
REV,REPORT_TIME,VEHICLE_TAG,LONGITUDE,LATITUDE,SPEED,HEADING,TRAIN_ASSIGNMENT,PREDICTABLE

1485,01/01/2015 16:10:59,02,-122.41961,37.80203,0.833,350.0,5904,0

1485,01/01/2015 16:11:14,02,-122.4197,37.80245,3.889,350.0,5904,0

1485,01/01/2015 16:12:12,02,-122.42003,37.80416,3.333,350.0,5904,0

1485,01/01/2015 16:12:29,02,-122.42016,37.80478,2.5,351.0,5904,0
```

Visualization of data with CartoDB:

Plan of attack:
- Model each route
- Target: arrival time at a given stop
- Features: location, speed, time of day, weather

There are several approaches toward modeling estimated time of arrival (ETA)4,5,6,7. It seems that most models involve dividing each route into segments, then predicting the remaining travel time along a segment based on current speed, distance along the segment, and historical travel times for that segment at that time of day. More complicated models include performance on previous segments of the route.

Other models involve constructing a graph with stops as nodes and with the edges weighted according to historical travel times and other features. Such a graph would also facilitate finding the quickest path between destinations in goal #2.

I plan to further investigate ETA modeling methods and algorithms, formulate an approach based on some combination of methods, and try several treatments of the data.

Challenges:
- I would like to incorporate ridership data into my models, since that would be quite a significant feature, but the only Muni data I can find is from 2006-20078.
- Routes change or disappear over time, and new routes appear9. How do I best account for this in my models? Fitting to route segments seems to be the best approach, but if a new segment shows up, users will just have to wait until there's enough data for a good prediction.
Sources:
Bus GPS data from Aug 2012 to the present
ftp://avl-data.sfmta.com/AVL_DATA/

Real-time bus GPS data
http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

Routes & Schedules
https://www.sfmta.com/about-sfmta/reports/gtfs-transit-data

Weather data
https://www.ncdc.noaa.gov/homr/api
	Downtown SF: http://www.ncdc.noaa.gov/homr/services/station/20002487

CartoDB for route visualizations
https://cartodb.com/


[1]: https://www.sfmta.com/about-sfmta/reports/performance-metrics/percentage-time-performance

[NextBus]: http://nextbus.cubic.com/About/How-NextBus-Works

3. “San Francisco Transit Prediction Accuracy”
https://goswift.ly/blog/2015/12/23/san-francisco-transit-prediction-accuracy-how-swyft-helps-you-commute-smarter-1

4. Sun et al, 2007, “Predicting Bus Arrival Time on the Basis of Global Positioning System Data”
https://www.researchgate.net/publication/245562763_Predicting_Bus_Arrival_Time_on_the_Basis_of_Global_Positioning_System_Data

5. Shalaby, Farhan, 2004, “Prediction Model of Bus Arrival and Departure Times Using AVL and APC Data”
http://www.nctr.usf.edu/wp-content/uploads/2010/03/JPT-7-1-Shalaby.pdf

6. Kidwell, 2001, “Predicting Transit Vehicle Arrival Times”
http://www.glump.net/content/bus_predict/predicting_transit_vehicle_arrivals.htm

7. Baker, Nied, 2013, “Predicting Bus Arrivals Using One Bus Away Real-Time Data”
http://homes.cs.washington.edu/~anied/papers/AConradNied_OneBusAway_Writeup_20131209.pdf

8. Transit Effectiveness Project (TEP) Passenger Data
http://archives.sfmta.com/cms/rtep/tepdataindx.htm

9. Information about upcoming SF Muni route changes
https://www.sfmta.com/projects-planning/projects/muni-forward-0
