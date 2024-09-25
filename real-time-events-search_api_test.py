import requests

# for now it only fetches and displays concert information for a specified location 

def get_concerts(location):
    url = "https://real-time-events-search.p.rapidapi.com/search-events"
    querystring = {
        "query": f"concerts in {location}",
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
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    location = input("Enter the location (e.g., 'San Francisco'): ").strip()
    get_concerts(location)


# example 
