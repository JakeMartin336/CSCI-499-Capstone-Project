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
def setup_faiss_index():
    global user_data, user_embeddings, user_ids, faiss_index, recommendation_history

    # Load user data
    with open('users_data.json', 'r') as file:
        user_data = json.load(file)

    user_embeddings = []
    user_ids = []

    for user in user_data:
        if user['survey_complete']:  # Only consider users with complete surveys
            embedding = generate_user_vector(user)
            user_embeddings.append(embedding)
            user_ids.append(user['id'])

    # Convert list of embeddings to numpy array
    user_embeddings = np.array(user_embeddings, dtype='float32')

    # Set up Faiss index for similarity search
    dimension = user_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(user_embeddings)  # Add user embeddings to the index

    # Initialize recommendation history
    recommendation_history = load_recommendation_history()
    print("FAISS index and recommendation history initialized.")


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
        return None, , "No new matches available at the moment." 

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
    return None, , "No new matches available at the moment."   # If no valid match is found --> think of soemthing else we want to replace with 


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
