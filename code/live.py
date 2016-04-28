import requests
from bs4 import BeautifulSoup


# Querying live position data
live_url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=sf-muni'
response = requests.get(live_url)
soup = BeautifulSoup(response.text, 'lxml')
soup.findAll('vehicle')[0]['lat']
