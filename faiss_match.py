import openai
import numpy as np
import faiss 
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
import random

load_dotenv()
# Load your OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")

# Sample JSON data
# user_data = [
#     {
#         "id": 1,
#         "created_at": "2024-10-16T18:08:41.011763+00:00",
#         "user_name": "Jacob Martin",
#         "age": 24,
#         "email_address": "jacob.martin@example.com",
#         "account_description": "I love rock music",
#         "user_location": "manhattan",
#         "music_genre": [
#             "rock",
#             "jazz"
#         ],
#         "budget": "100.00",
#         "contacts": [
#             2
#         ],
#         "password": "password123",
#         "travel_time": None,
#         "survey_complete": True
#     },
#     {
#         "id": 2,
#         "created_at": "2024-10-16T18:08:41.096985+00:00",
#         "user_name": "Tim Bob",
#         "age": 78,
#         "email_address": "temp@temp.com",
#         "account_description": "Old in age but young at heart",
#         "user_location": "Brooklyn",
#         "music_genre": [
#             "Metal",
#             "Hip-Hop"
#         ],
#         "budget": "250.00",
#         "contacts": [
#             1
#         ],
#         "password": "temp_pass",
#         "travel_time": None,
#         "survey_complete": True
#     },
#     {
#         "id": 3,
#         "created_at": "2024-10-16T18:08:41.183195+00:00",
#         "user_name": "Emily Chen",
#         "age": 29,
#         "email_address": "emily.chen@example.com",
#         "account_description": "Avid traveler and food lover",
#         "user_location": "brooklyn",
#         "music_genre": [
#             "pop",
#             "classical"
#         ],
#         "budget": "150.00",
#         "contacts": [],
#         "password": "123password",
#         "travel_time": None,
#         "survey_complete": True
#     },
#     {
#         "id": 4,
#         "created_at": "2024-10-16T18:09:54.305771+00:00",
#         "user_name": "Sara Lee",
#         "age": 30,
#         "email_address": "sara.lee@example.com",
#         "account_description": "Coffee enthusiast and book lover",
#         "user_location": "Manhattan",
#         "music_genre": [
#             "Jazz",
#             "Classical"
#         ],
#         "budget": "120.00",
#         "contacts": [],
#         "password": "pass_temp",
#         "travel_time": None,
#         "survey_complete": True
#     },
#     {
#         "id": 8,
#         "created_at": "2024-10-23T21:58:19.702737+00:00",
#         "user_name": "Krabs",
#         "age": 44,
#         "email_address": "krabs@krabs.com",
#         "account_description": "Krabs, krabs, krabs",
#         "user_location": "Brooklyn",
#         "music_genre": [
#             "Country",
#             "Hip-Hop/Rap",
#             "Jazz"
#         ],
#         "budget": "100-300",
#         "contacts": None,
#         "password": "krabs",
#         "travel_time": "1-3hr",
#         "survey_complete": True
#     },
#     {
#         "id": 9,
#         "created_at": "2024-10-31T01:16:36.814018+00:00",
#         "user_name": "ninh",
#         "age": 25,
#         "email_address": "ninh@gmail.com",
#         "account_description": "",
#         "user_location": "Brooklyn",
#         "music_genre": [
#             "Ballads/Romantic",
#             "Hip-Hop/Rap",
#             "Pop"
#         ],
#         "budget": "0-100",
#         "contacts": None,
#         "password": "12345",
#         "travel_time": "0-1hr",
#         "survey_complete": True
#     },
#     {
#         "id": 12,
#         "created_at": "2024-11-01T23:40:18.618887+00:00",
#         "user_name": "KimKard",
#         "age": 43,
#         "email_address": "KK@example.com",
#         "account_description": "Hello I am Kim Kardashian! I love music!",
#         "user_location": "Manhattan",
#         "music_genre": [
#             "Children\u2019s music",
#             "Dance/Electronic",
#             "Pop"
#         ],
#         "budget": "500+",
#         "contacts": None,
#         "password": "kanyewest",
#         "travel_time": "3+ hr",
#         "survey_complete": True
#     },
#     {
#         "id": 13,
#         "created_at": "2024-11-11T19:54:29.019431+00:00",
#         "user_name": "hi ",
#         "age": 25,
#         "email_address": "test@gmail.com",
#         "account_description": "test",
#         "user_location": "Manhattan",
#         "music_genre": [
#             "Alternative",
#             "Blues",
#             "Classic"
#         ],
#         "budget": "100-300",
#         "contacts": None,
#         "password": "test",
#         "travel_time": "1-3hr",
#         "survey_complete": True
#     },
#     {
#         "id": 15,
#         "created_at": "2024-11-12T00:56:39.134603+00:00",
#         "user_name": "hi1",
#         "age": 25,
#         "email_address": "test1@gmail.com",
#         "account_description": "I love 90s Rock! :3 ",
#         "user_location": "Brooklyn",
#         "music_genre": [
#             "Alternative",
#             "Other",
#             "Rock"
#         ],
#         "budget": "100-300",
#         "contacts": None,
#         "password": "2",
#         "travel_time": "0-1hr",
#         "survey_complete": True
#     },
#     {
#         "id": 17,
#         "created_at": "2024-11-12T19:38:11.809049+00:00",
#         "user_name": "ttt",
#         "age": None,
#         "email_address": "tes2t@gmail.com",
#         "account_description": None,
#         "user_location": None,
#         "music_genre": None,
#         "budget": None,
#         "contacts": None,
#         "password": "q",
#         "travel_time": None,
#         "survey_complete": False
#     },
#     {
#         "id": 18,
#         "created_at": "2024-11-13T00:02:06.589987+00:00",
#         "user_name": "test3@gmail.com",
#         "age": 25,
#         "email_address": "test3@gmail.com",
#         "account_description": "sws",
#         "user_location": "Queens",
#         "music_genre": [
#             "Classic"
#         ],
#         "budget": "300-500",
#         "contacts": None,
#         "password": "test",
#         "travel_time": "0-1hr",
#         "survey_complete": True
#     },
#     {
#         "id": 19,
#         "created_at": "2024-11-11T19:54:29.019431+00:00",
#         "user_name": "hi ",
#         "age": 25,
#         "email_address": "test@gmail.com",
#         "account_description": "test",
#         "user_location": "Manhattan",
#         "music_genre": [
#             "Alternative",
#             "Blues",
#             "Classic"
#         ],
#         "budget": "100-300",
#         "contacts": None,
#         "password": "test",
#         "travel_time": "1-3hr",
#         "survey_complete": True
#     },
#     {
#         "id": 20,
#         "created_at": "2024-10-31T01:16:36.814018+00:00",
#         "user_name": "ninh",
#         "age": 25,
#         "email_address": "ninh@gmail.com",
#         "account_description": "",
#         "user_location": "Brooklyn",
#         "music_genre": [
#             "Ballads/Romantic",
#             "Hip-Hop/Rap",
#             "Pop"
#         ],
#         "budget": "0-100",
#         "contacts": None,
#         "password": "12345",
#         "travel_time": "0-1hr",
#         "survey_complete": True
#     }
# ]


client = OpenAI(
    api_key=openai_key,
)

def load_recommendation_history(filename='recommendation_history_3.json'):
    # Load recommendation history from a JSON file.
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return {}  # Return an empty dictionary if no file exists

def save_recommendation_history(history, filename='recommendation_history_3.json'):
    # Save recommendation history to a JSON file.
    with open(filename, 'w') as file:
        json.dump(history, file)

def generate_user_vector(user):
    #Generate a text description for user attributes and get embeddings.
    # Handle None values to avoid errors
    user_description = (
        f"User {user.get('user_name', 'Unknown')} is {user.get('age', 'unknown')} years old from {user.get('user_location', 'an unknown location')}. "
        f"They love {', '.join(user.get('music_genre', [])) or 'no specific genre'} music and have a budget of {user.get('budget', 'unknown')}. "
        f"Travel time preference is {user.get('travel_time', 'unspecified')}. "
        f"Additional description: {user.get('account_description', 'No additional description')}."
    )
    
    # Generate embedding using OpenAI API + the user text
    response = client.embeddings.create(
        input=user_description,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    
    return np.array(embedding)

# Step 1: Generate embeddings for each user
with open('users_data.json', 'r') as file:
    user_data = json.load(file)

user_embeddings = []
user_ids = []

for user in user_data:
    if user['survey_complete']:  # Only consider users with complete surveys or we can include everyone
        embedding = generate_user_vector(user)
        user_embeddings.append(embedding)
        user_ids.append(user['id'])

# Convert list of embeddings to numpy array
user_embeddings = np.array(user_embeddings, dtype='float32')

# Step 2: Set up Faiss index for similarity search
dimension = user_embeddings.shape[1] 
faiss_index = faiss.IndexFlatL2(dimension)  
faiss_index.add(user_embeddings)  # Add user embeddings to the index

# Initialize a dictionary to store recommendation history
recommendation_history = load_recommendation_history()


# this is an optional function if we want to use explanation from openAI
def explain_recommendation(target_user, matched_user):
    # Use OpenAI chat feature to generate a explanation for the match.
    prompt = (
        f"I have a user named {target_user['user_name']} who likes {', '.join(target_user['music_genre'])} music "
        f"and is located in {target_user['user_location']}. They have a budget of {target_user['budget']} "
        f"and a travel time preference of {target_user['travel_time']}. "
        f"I want to match them with {matched_user['user_name']} who likes {', '.join(matched_user['music_genre'])} "
        f"music and is located in {matched_user['user_location']}. They have a budget of {matched_user['budget']} "
        f"and a travel time preference of {matched_user['travel_time']}. "
        f"Why would this be a good match?"
    )
    
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=100
    )
    
    return response.choices[0].text

# We are using this version with explanation rn
def recommend_best_match_faiss(target_id):
    # Recommend the best user match using Faiss similarity search, avoiding duplicates by using a history
    target_user = next((user for user in user_data if user['id'] == target_id), None)
    if not target_user or not target_user['survey_complete']:
        return None

    # Generate vector for the target user
    target_vector = generate_user_vector(target_user).reshape(1, -1)
    
    # Perform similarity search | fetch recommendation history to avoid recommending the same people
    D, index = faiss_index.search(target_vector, k=len(user_ids))  # Search all users
    recommendation_history_for_user = recommendation_history.get(str(target_id), [])
    
    print(f"Recommendation history before updating for user {target_id}: {recommendation_history_for_user}")
    
    # Iterate through the results, skipping already recommended users
    for idx in index[0]:
        matched_user_id = user_ids[idx]
        
        # Skip if the match is the target user or if they have been recommended already
        if matched_user_id != target_id and matched_user_id not in recommendation_history_for_user:
            # Make sure the key is a string to avoid issues with JSON serialization
            target_id_str = str(target_id)
            
            # Append to the list if the key exists, if not create a new key:val pair
            if target_id_str in recommendation_history:
                recommendation_history[target_id_str].append(matched_user_id)
            else:
                recommendation_history[target_id_str] = [matched_user_id]
            
            # Save updated recommendation history to file
            save_recommendation_history(recommendation_history)
            
            print(f"Updated recommendation history for user {target_id}: {recommendation_history[target_id_str]}")
            
            # Get the matched user details & skip first since it is the same user
            matched_user = next(user for user in user_data if user['id'] == matched_user_id)
            
            # Generate a recommendation explanation using OpenAI --> this is optional but if we want to include a short explanation of why this person, it would be nice to have 
            explanation = explain_recommendation(target_user, matched_user)
            
            # print(f"Explanation for the match between {target_user['user_name']} and {matched_user['user_name']}:\n{explanation}")
            
            return matched_user, explanation
    
    # If no match is found, just print out no match found --> we want to try to avoid this tho 
    print(f"No new match found for user {target_id}")
    return None  # If no valid match is found --> think of soemthing else we want to replace with 


# Example for users
# best_match, explanation= recommend_best_match_faiss(1)
# if best_match:
#     print(f"Best match for given user is: {best_match['user_name']}\nExplanation: {explanation}")
# else:
#     print("No new match found.")

##### We can also hav this version of the function where there is not explanation ###
def recommend_best_match_faiss_1(target_id):
    target_user = next((user for user in user_data if user['id'] == target_id), None)
    if not target_user or not target_user['survey_complete']:
        return None

    target_vector = generate_user_vector(target_user).reshape(1, -1)
    
    D, I = faiss_index.search(target_vector, k=len(user_ids))  
    recommendation_history_for_user = recommendation_history.get(str(target_id), [])
    
    print(f"Recommendation history before updating for user {target_id}: {recommendation_history_for_user}")
    
    for idx in I[0]:
        matched_user_id = user_ids[idx]
        
        if matched_user_id != target_id and matched_user_id not in recommendation_history_for_user:
            target_id_str = str(target_id)
            
            if target_id_str in recommendation_history:
                recommendation_history[target_id_str].append(matched_user_id)
            else:
                recommendation_history[target_id_str] = [matched_user_id]
            
            save_recommendation_history(recommendation_history)
            
            print(f"Updated recommendation history for user {target_id}: {recommendation_history[target_id_str]}")
            
            matched_user = next(user for user in user_data if user['id'] == matched_user_id)
            return matched_user
    
    print(f"No new match found for user {target_id}")
    return None 

# best_match = recommend_best_match_faiss(13)
# if best_match:
#     print(f"Best match for user id 9 is: {best_match['user_name']}")
# else:
#     print("No new match found.")