import requests

def get_concerts(location, artist):
    url = "https://real-time-events-search.p.rapidapi.com/search-events"
    querystring = {
        "query": f"{artist} concerts in {location}",
        "date": "any",
        "is_virtual": "false",
        "start": "0"
    }
    
    headers = {
        "x-rapidapi-host": "real-time-events-search.p.rapidapi.com",
        "x-rapidapi-key": "d70791e08amsh1cd03ce9f9fdc97p1f97d4jsn378f66394a3e"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        
        if "data" in data and data["data"]:
            found_event = False
            for event in data["data"]:
                # Check if the artist's name is in the event's name/title
                event_name = event.get('name', '').lower()
                
                if artist.lower() in event_name:
                    found_event = True
                    # Display concert details in a clean and standard form
                    print(f"Event: {event['name']}")
                    print(f"Description: {event.get('description', 'No description available')}")
                    print(f"Start Time: {event.get('start_time', 'Not specified')}")
                    print(f"End Time: {event.get('end_time', 'Not specified')}")
                    venue = event.get('venue', {})
                    print(f"Venue: {venue.get('name', 'Unknown venue')} - {venue.get('full_address', 'Address not available')}")
                    if event.get('info_links'):
                        print(f"More Info: {event['info_links'][0]['link']}")
                    print("-" * 40)
            
            if not found_event:
                print(f"No events found for {artist} performing in {location}.")
        else:
            print("No events found.")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    location = input("Enter the location (e.g., 'New York'): ").strip()
    artist = input("Enter the artist's name: ").strip()
    
    get_concerts(location, artist)
