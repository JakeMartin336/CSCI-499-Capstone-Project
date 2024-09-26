import requests
import json

# FOR EVENTS FOR ARTISTS
def get_artist(artist=None):
    url_artist = "https://concerts-artists-events-tracker.p.rapidapi.com/artist"

    querystring = {
        # "name":"Ed sheeran",
        'name': artist,
        "page":"1",
    }

    headers = {
        "x-rapidapi-host": "concerts-artists-events-tracker.p.rapidapi.com",
        "x-rapidapi-key": "d70791e08amsh1cd03ce9f9fdc97p1f97d4jsn378f66394a3e"
    }

    response = requests.get(url_artist, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        # print(json.dumps(data, indent=4))

        if "data" in data and data["data"]:
            for event in data["data"]:
                print(f"Event: {event['name']}")
                print(f"Description: {event.get('description', 'No description available')}")
                print(f"Start Time: {event.get('start_time', 'Not specified')}")
                print(f"End Time: {event.get('end_time', 'Not specified')}")
                venue = event.get('venue', {})
                print(f"Venue: {venue.get('name', 'Unknown venue')} - {venue.get('full_address', 'Address not available')}")
                if event.get('info_links'):
                    print(f"More Info: {event['info_links'][0]['link']}")
                print("-" * 40)
        else:
            print("No events found.")

    else:
        print(f"Error: {response.status_code}")
    
    return data

# FOR EVENTS BY LOCATION
def get_location(location=None):
    url_location = "https://concerts-artists-events-tracker.p.rapidapi.com/location"

    querystring = {
        # "name":"Paris",
        'name' : location,
        "minDate":"2024-10-01",
        "maxDate":"2024-11-08",
        "page":"1"}

    headers = {
        "x-rapidapi-host": "concerts-artists-events-tracker.p.rapidapi.com",
        "x-rapidapi-key": "d70791e08amsh1cd03ce9f9fdc97p1f97d4jsn378f66394a3e"
    }

    response = requests.get(url_location, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        # print(json.dumps(data, indent=4))
        
        if "data" in data and data["data"]:
            for event in data["data"]:
                print(f"Event: {event['name']}")
                print(f"Description: {event.get('description', 'No description available')}")
                print(f"Start Time: {event.get('start_time', 'Not specified')}")
                print(f"End Time: {event.get('end_time', 'Not specified')}")
                venue = event.get('venue', {})
                print(f"Venue: {venue.get('name', 'Unknown venue')} - {venue.get('full_address', 'Address not available')}")
                if event.get('info_links'):
                    print(f"More Info: {event['info_links'][0]['link']}")
                print("-" * 40)
        else:
            print("No events found.")

    else:
        print(f"Error: {response.status_code}")
    
    return data

# FOR EVENTS BY VENUE
def get_venue(venue=None):
    url_venue = "https://concerts-artists-events-tracker.p.rapidapi.com/venue"

    querystring = {
        # "name":"Hollywood bowl",
        'name': venue,
        "page":"1",
    }

    headers = {
        "x-rapidapi-host": "concerts-artists-events-tracker.p.rapidapi.com",
        "x-rapidapi-key": "d70791e08amsh1cd03ce9f9fdc97p1f97d4jsn378f66394a3e"
    }

    response = requests.get(url_venue, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        
        print(json.dumps(data, indent=4))
        
        if "data" in data and data["data"]:
            for event in data["data"]:
                print(f"Event: {event['name']}")
                print(f"Description: {event.get('description', 'No description available')}")
                print(f"Start Time: {event.get('start_time', 'Not specified')}")
                print(f"End Time: {event.get('end_time', 'Not specified')}")
                venue = event.get('venue', {})
                print(f"Venue: {venue.get('name', 'Unknown venue')} - {venue.get('full_address', 'Address not available')}")
                if event.get('info_links'):
                    print(f"More Info: {event['info_links'][0]['link']}")
                print("-" * 40)
        else:
            print("No events found.")

    else:
        print(f"Error: {response.status_code}")
    
    return data

def main():
    get_artist('Ed sheeran')
    get_location('Paris')
    get_venue('Hollywood Bowl')

if __name__ == "__main__":
    main()
