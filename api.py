import requests

def get_concerts(genre, location, budget=0):
    url = "https://real-time-events-search.p.rapidapi.com/search-events"
    querystring = {
        "query": f"{genre} concert in {location}",
        "date": "any",
        "is_virtual": "false",
        "start": "0"
    }
    
    headers = {
        "x-rapidapi-host": "real-time-events-search.p.rapidapi.com",
        "x-rapidapi-key": "d50f6e803emsh4e674004cf2581ep178d33jsne1cea532c048",
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        
        if "data" in data and data["data"]:
            final_events = []
            for event in data["data"]:
                curr_event = []
                event_name = event.get('name', 'Not specified')
                event_description = event.get('description', 'No description available')
                event_start = event.get('start_time', 'Not specified')
                # event_thumbnail = {event.get('thumbnail', 'Not specified')}
                # event_ticket_links = {event.get('ticket_links', 'Not specified')}
                venue = event.get('venue', {})
                venue_info = f"{venue.get('name', 'Unknown venue')} - {venue.get('full_address', 'Address not available')} - {venue.get('website', 'Not specified')}"
                
                curr_event.append(event_name)
                curr_event.append(event_description)
                curr_event.append(event_start)
                curr_event.append(venue_info)

                final_events.append(curr_event)
       
        else:
            print("No events found.")
    else:
        print(f"Error: {response.status_code}")

    for temp in final_events:
        print(temp,'\n')