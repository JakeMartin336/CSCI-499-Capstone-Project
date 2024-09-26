import requests
import json

API_KEY = 'bv3fIbkBp4hjBLjVOBBessILI48oEYGG'

url_attractions = 'https://app.ticketmaster.com/discovery/v2/attractions.json'
url_classifications = 'https://app.ticketmaster.com/discovery/v2/classifications.json'

# 'segment': {'id': 'KZFzniwnSyZfZ7v7nJ', 'name': 'Music'}

def get_events(key_word=None, classification=None, attraction=None, radius=None):
    
    ur_event = 'https://app.ticketmaster.com/discovery/v2/events.json'

    params = {
        'apikey': API_KEY,
        'keyword': key_word,
        'classificationId': classification,
        'attractionId' : attraction,  
        'city': 'New York',
        'radius' : radius,
        'unit' : 'miles',
    }

    response = requests.get(ur_event, params=params)


    if response.status_code == 200:
        data = response.json()

        # for event in data['_embedded']['events']:
        #     print(f"Event: {event['name']}")
        #     print(f"Date: {event['dates']['start']['localDate']}")
        #     print(f"Venue: {event['_embedded']['venues'][0]['name']}")
        #     print(f"City: {event['_embedded']['venues'][0]['city']['name']}\n")

        # if '_embedded' in data and 'events' in data['_embedded']:
        #     event = data['_embedded']['events'][0]
        
        for event in data['_embedded']['events']:
            
            # Event Information
            name = event.get('name', 'N/A')
            event_url = event.get('url', 'N/A')

            print(f"Event Information:\n- Name: {name}\n- URL: {event_url}")

            # Sales Information
            presales = event.get('sales', {}).get('presales', 'N/A')
            price_ranges = event.get('priceRanges', 'N/A')
            
            if presales != 'N/A':
                presales_info = ", ".join([pre['name'] for pre in presales])
            else:
                presales_info = "N/A"

            if price_ranges != 'N/A':
                price_info = f"${price_ranges[0]['min']} - ${price_ranges[0]['max']}"
            else:
                price_info = "N/A"
            
            print(f"Sales Information:\n- Presales: {presales_info}\n- Price Range: {price_info}")

            # Date and Time
            dates = event.get('dates', {}).get('start', {})
            local_date = dates.get('localDate', 'N/A')
            local_time = dates.get('localTime', 'N/A')
            onsale_status = event.get('dates', {}).get('status', {}).get('code', 'N/A')

            print(f"Date and Time:\n- Local Date: {local_date}\n- Local Time: {local_time}\n- On-Sale Status: {onsale_status}")

            # Classifications
            classifications = event.get('classifications', [{}])[0]
            genre = classifications.get('genre', {}).get('name', 'N/A')
            subgenre = classifications.get('subGenre', {}).get('name', 'N/A')

            print(f"Classifications:\n- Genre: {genre}\n- SubGenre: {subgenre}")

            # Venue Details
            venues = event.get('_embedded', {}).get('venues', [{}])[0]
            venue_name = venues.get('name', 'N/A')
            address = venues.get('address', {}).get('line1', 'N/A')
            city = venues.get('city', {}).get('name', 'N/A')
            state = venues.get('state', {}).get('name', 'N/A')

            print(f"Venue Details:\n- Venue Name: {venue_name}\n- Address: {address}, {city}, {state}")
            print('\n\n')

    else:
        print(f"Error: {response.status_code} - {response.text}")

    return None


def get_classification_id():
    url = url_classifications
    params = {
        'apikey': API_KEY,
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # pretty_json = json.dumps(classifications, indent=4)
        # print(pretty_json)
        # with open('classification_output.json', 'w') as json_file:
        #     json.dump(data, json_file, indent=4)
        
        for classification in data.get('_embedded', {}).get('classifications', []):
            if classification.get('segment', {}).get('name') == 'Music':
                class_music = classification
        
        music_list = []
        for genre in class_music['segment']['_embedded']['genres']:
            genre_and_id = (genre['name'], genre['id'])
            music_list.append(genre_and_id)
        # print(music_list,'\n\n')

#########################################################################################
        for classification in data.get('_embedded', {}).get('classifications', []):
            if classification.get('type', {}).get('name') == 'Individual':
                class_individual = classification
        indiv_list = []
        for indiv in class_individual['type']['_embedded']['subtypes']:
            if indiv.get('name') in (["Artist", "Musician", "Performer", "Singer/Vocalist"]):
                indiv_and_id = (indiv['name'], indiv['id'])
                indiv_list.append(indiv_and_id)
        # print(indiv_list,'\n\n')

#########################################################################################
        for classification in data.get('_embedded', {}).get('classifications', []):
            if classification.get('type', {}).get('name') == 'Group':
                class_group = classification
        group_list = []
        for group in class_group['type']['_embedded']['subtypes']:
            if group.get('name') in (["Band", "Group", "Tribute Band"]):
                group_and_id = (group['name'], group['id'])
                group_list.append(group_and_id)
        # print(group_list,'\n\n')

#########################################################################################
        for classification in data.get('_embedded', {}).get('classifications', []):
            if classification.get('type', {}).get('name') == 'Event Style':
                class_event = classification
        event_list = []
        for event in class_event['type']['_embedded']['subtypes']:
            if event.get('name') in (["Concert", "Fan Experiences", "Festival", "Party/Gala", ]):
                event_and_id = (event['name'], event['id'])
                event_list.append(event_and_id)
        # print(event_list,'\n\n')
    
    else:
        print(f"Error retrieving classifications: {response.status_code} - {response.text}")
    
    return music_list,indiv_list,group_list,event_list


def get_attraction_id():
    url = url_attractions
    params = {
        'apikey': API_KEY,
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # pretty_json = json.dumps(classifications, indent=4)
        # print(pretty_json)
        # with open('classification_output.json', 'w') as json_file:
        #     json.dump(data, json_file, indent=4)
        
        attract_list = []
        for attraction in data.get('_embedded', {}).get('attractions', []):
            for classification in attraction.get("classifications", []):
                segment = classification.get("segment", {})
                if segment.get('name') == 'Music':
                    attract_and_id = (attraction['name'], classification.get("genre", {}).get("name"), attraction['id'])
                    attract_list.append(attract_and_id)
                    break

        # print(attract_list,'\n\n')
    else:
        print(f"Error retrieving attractions: {response.status_code} - {response.text}")
    
    return attract_list

def get_suggested():
    url = 'https://app.ticketmaster.com/discovery/v2/suggest.json'

    params = {
        'apikey': API_KEY,
        'city': 'New York',
        'keyword' : 'Rock',
    }

    response = requests.get(url, params=params)

    data = response.json()  

    # with open('suggest_output.json', 'w') as json_file:
    #     json.dump(data, json_file, indent=4)

def main():
    print('\n')
    key_word = 'music' 
    music_list,indiv_list,group_list,event_list = get_classification_id()
    attract_list = get_attraction_id()
    radius = '10'
    temp = get_events(key_word, 'KnvZfZ7vAv1', None, radius)


if __name__ == '__main__':
    main()