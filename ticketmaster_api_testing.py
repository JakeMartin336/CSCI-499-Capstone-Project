import requests
import random

API_KEY = 'bv3fIbkBp4hjBLjVOBBessILI48oEYGG'

url = 'https://app.ticketmaster.com/discovery/v2/events.json'

params = {
    'apikey': API_KEY,
    'keyword': 'music',  
    'city': 'New York',
    'size': 5  
}


response = requests.get(url, params=params)


if response.status_code == 200:
    data = response.json()
    
    for event in data['_embedded']['events']:
        print(f"Event: {event['name']}")
        print(f"Date: {event['dates']['start']['localDate']}")
        print(f"Venue: {event['_embedded']['venues'][0]['name']}")
        print(f"City: {event['_embedded']['venues'][0]['city']['name']}\n")
else:
    print(f"Error: {response.status_code} - {response.text}")
