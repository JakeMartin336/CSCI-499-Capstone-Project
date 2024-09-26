import requests

# Replace with your personal OAuth token
API_KEY = "7ZYIC5YCFCWIXI2J3ECH"
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Define search parameters for concerts
params = {
    "q": "concert",
    "categories": "103",  # Music category
    "location.address": "New York",  # Replace with desired location
    "start_date.range_start": "2024-09-01T00:00:00Z",  # Date range (optional)
    "start_date.range_end": "2024-12-31T23:59:59Z"
}

# Make the request to search for events
response = requests.get("https://www.eventbriteapi.com/v3/events/search/", headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    events = data.get('events', [])
    for event in events:
        print(f"Event Name: {event['name']['text']}")
        print(f"Start Time: {event['start']['local']}")
        print(f"Venue: {event['venue_id']}")
        print("--------")
else:
    print(f"Error: {response.status_code}, {response.text}")
