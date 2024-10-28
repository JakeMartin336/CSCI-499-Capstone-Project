import requests

def get_concerts(genre, location, budget=0):
    final_events = []

    url = "https://real-time-events-search.p.rapidapi.com/search-events"
    querystring = {
        "query": f"{genre} concert in {location}",
        "date": "any",
        "is_virtual": "false",
        "start": "0"
    }
    
    headers = {
        "x-rapidapi-host": "real-time-events-search.p.rapidapi.com",
        # "x-rapidapi-key": "d50f6e803emsh4e674004cf2581ep178d33jsne1cea532c048",
        "x-rapidapi-key": "d70791e08amsh1cd03ce9f9fdc97p1f97d4jsn378f66394a3e",
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]:
            for event in data["data"]:
                curr_event = {
                    "name": event.get('name', 'Not specified'),
                    "description": event.get('description', 'No description available'),
                    "start_time": event.get('start_time', 'Not specified'),
                    'thumbnail': event.get('thumbnail', 'Not specified'),
                    "venue": {
                        "name": event.get('venue', {}).get('name', 'Unknown venue'),
                        "address": event.get('venue', {}).get('full_address', 'Address not available'),
                        "website": event.get('venue', {}).get('website', 'Not specified')
                    }
                }
                final_events.append(curr_event)
        else:
            print("No events found.")
    else:
        print(f"Error: {response.status_code}")
    
    return final_events


# if __name__ == '__main__':
#     concerts_by_genre = get_concerts('rock', 'manhattan')
#     print(concerts_by_genre)


def example_concerts():
    events_data = (
        [
            {
                'name': 'Donovan Woods, Katelyn Tarver',
                'description': "Donovan Woods has partnered with PLUS1 to donate $1 from every ticket to MusiCares, supporting the music community's health and well-being.",
                'start_time': '2024-11-02 18:30:00',
                'thumbnail': 'https://i.scdn.co/image/ab6761860000101631346f09787e3b8ecd149e13',
                'venue': {
                    'name': 'LPR',
                    'address': '158 Bleecker Street, New York, NY 10012, United States',
                    'website': 'http://lpr.com/'
                }
            },
            {
                'name': 'Wynton Marsalis',
                'description': "The JLCO with Wynton Marsalis and Grammy-nominated bassist Carlos Henriquez explore Afro-Cuban sounds, sharing stories behind patterns, melodies, and the music's history.",
                'start_time': '2024-11-23 14:00:00',
                'thumbnail': 'https://i.scdn.co/image/ab676186000010164b04d8f49733fff23c6e4b7c',
                'venue': {
                    'name': 'The Appel Room',
                    'address': '10 Columbus Circle, New York, NY 10019, United States',
                    'website': 'http://www.jazz.org/venues/the-appel-room-64/'
                }
            },
            {
                'name': 'Iron Maiden',
                'description': "Prepare for Iron Maiden's most explosive live show, with their The Future Past tour featuring more Pyro, effects, and a replica Spitfire, making it a must-see for fans.",
                'start_time': '2024-11-02 19:30:00',
                'thumbnail': 'https://i.scdn.co/image/ab67618600001016ba75a0bd1babf4d7a7a1153f',
                'venue': {
                    'name': 'Barclays Center',
                    'address': 'Address not available',
                    'website': 'http://www.barclayscenter.com/'
                }
            },
            {
                'name': 'The Rock & Roll Playhouse',
                'description': "Enjoy The Rock and Roll Playhouse plays the Music of Rihanna + More for Kids at Brooklyn Bowl in Brooklyn, NY.",
                'start_time': '2024-11-10 12:00:00',
                'thumbnail': 'https://i.scdn.co/image/ab67618600001016ee3e5f686526f8138e7be8b3',
                'venue': {
                    'name': 'Brooklyn Bowl',
                    'address': '61 Wythe Avenue, Brooklyn, NY 11249, United States',
                    'website': 'http://www.brooklynbowl.com/brooklyn'
                }
            },
            {
                'name': 'Hinds',
                'description': "Join the Hinds event at Warsaw in Brooklyn, NY, at 261 Driggs Ave, starting at 7:00 P.M. on October 29, 2024.",
                'start_time': '2024-10-29 19:00:00',
                'thumbnail': 'https://i.scdn.co/image/ab6761860000101662860bb3c59ee4c0ca8f55b0',
                'venue': {
                    'name': 'Warsaw Concerts',
                    'address': '261 Driggs Avenue, Brooklyn, NY 11222, United States',
                    'website': 'https://www.warsawconcerts.com/?utm_source=GMBlisting&utm_medium=organic'
                }
            },
            {
                'name': 'Mark Ambor',
                'description': "Catch Mark Ambor live at Irving Plaza in New York, NY, located at 17 Irving Place. The event begins at 7:00 P.M.",
                'start_time': '2024-12-03 19:00:00',
                'thumbnail': 'https://s1.ticketm.net/dam/a/a4c/91958616-47f5-4f7c-92e8-64ad94b9ea4c_CUSTOM.jpg',
                'venue': {
                    'name': 'Irving Plaza',
                    'address': '17 Irving Place, New York, NY 10003, United States',
                    'website': 'https://www.irvingplaza.com/?utm_source=GMBlisting&utm_medium=organic'
                }
            },
            {
                'name': 'The String Cheese Incident',
                'description': "Join The String Cheese Incident with special guests Stolen Gin at Brooklyn Paramount in Brooklyn, NY, located at 385 Flatbush Ave.",
                'start_time': '2024-10-30 18:00:00',
                'thumbnail': 'https://i.scdn.co/image/ab676186000010165f715ab09f44aca3e389b48a',
                'venue': {
                    'name': 'Brooklyn Paramount',
                    'address': 'Address not available',
                    'website': 'https://www.brooklynparamount.com/?utm_source=GMBlisting&utm_medium=organic'
                }
            },
            {
                'name': 'Wave To Earth',
                'description': "Following two nominations at the Korean Music Awards, indie rock band Wave to Earth heads to North America for a tour. Their debut album has garnered global acclaim.",
                'start_time': '2024-11-01 20:00:00',
                'thumbnail': 'https://i.scdn.co/image/ab6761860000101648debeebe74ebfe6f8747c86',
                'venue': {
                    'name': 'Hammerstein Ballroom at Manhattan Center',
                    'address': 'Address not available',
                    'website': 'http://mc34.com/'
                }
            },
            {
                'name': 'Strawberry Fields Ultimate Beatles Brunch Concert (Every Sunday)',
                'description': "Please note that brunch and gratuity are not included in the ticket price.",
                'start_time': '2024-11-24 11:30:00',
                'thumbnail': 'https://s3.eu-central-1.amazonaws.com/yt-s3/e99ed406-0166-4ad0-9090-ce7f79d20614.jpg',
                'venue': {
                    'name': 'City Winery New York City',
                    'address': '25 11th Avenue, New York, NY 10011, United States',
                    'website': 'https://citywinery.com/new-york-city?utm_source=gmb&utm_medium=local-seo&utm_campaign=city-winery-new-york-city'
                }
            }
        ]
    )
    return events_data
