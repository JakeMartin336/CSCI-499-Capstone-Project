import os
import numpy as np
import faiss
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from supabase import create_client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Supabase client and OpenAI embeddings
print("Initializing Supabase client...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

# Generate user profile prompt
def generate_user_profile_prompt(user):
    return f"This is a concert-goer named {user['user_name']}, aged {user['age']}, located in {user['user_location']}. They enjoy {', '.join(user['music_genre']) or 'No music genres specified'} music, have a budget of {user['budget']}, and prefer to travel within {user['travel_time']}. They have attended concerts like {', '.join(user['contacts']) or 'No past concerts listed'}."

# Fetch all user data from Supabase
def fetch_user_data():
    try:
        # Fetch data from the Supabase table
        print("Fetching user data...")
        response = supabase.table("users").select("*").execute()

        # Debugging: print response object
        print(f"Response from Supabase: {response}")

        # Check if data exists
        if 'data' not in response or not response['data']:
            print("No data found.")
            return None

        print("User data fetched successfully.")
        return response['data']  # Access the 'data' directly

    except Exception as e:
        print(f"An error occurred while fetching user data: {e}")
        return None

# Fetch user data by ID
def fetch_user_by_id(user_id):
    try:
        print(f"Fetching user with ID {user_id}...")
        # Fetch data by user_id
        response = supabase.table("users").select("*").eq("id", user_id).execute()

        # Check if there was an error
        if 'data' not in response or not response['data']:
            print(f"No user found with ID {user_id}.")
            return None

        print(f"User with ID {user_id} found: {response['data'][0]}")
        return response['data'][0]

    except Exception as e:
        print(f"An error occurred while fetching user with ID {user_id}: {e}")
        return None

# Update recommendation count in Supabase
def update_recommendation_count(user_id):
    user = fetch_user_by_id(user_id)
    if user:
        new_count = user.get("recommendation_count", 0) + 1
        response = supabase.table("users").update({"recommendation_count": new_count}).eq("id", user_id).execute()
        if 'data' not in response or response.get('error'):
            raise Exception(f"Error updating recommendation count: {response.get('error')}")
        print(f"Recommendation count updated for user {user_id}.")

# Generate embeddings for a user profile
def generate_user_embedding(user_profile_text):
    return embeddings.embed_query(user_profile_text)

# Create vector store
def create_vector_store(user_data):
    user_embeddings = []
    ids = []

    for user in user_data:
        profile_text = generate_user_profile_prompt(user)
        embedding = generate_user_embedding(profile_text)
        user_embeddings.append(embedding)
        ids.append(user["id"])

    user_embeddings_np = np.array(user_embeddings, dtype='float32')
    embedding_dim = user_embeddings_np.shape[1]

    index = faiss.IndexFlatL2(embedding_dim)
    index.add(user_embeddings_np)

    print("Vector store created with user embeddings.")
    return index, ids

# Find similar buddies
def find_similar_buddies(user_profile_text, vector_store, ids, max_matches=5):
    user_embedding = generate_user_embedding(user_profile_text)
    distances, indices = vector_store.search(np.array([user_embedding]), max_matches)

    matched_ids = [ids[idx] for idx in indices[0]]
    for match_id in matched_ids:
        update_recommendation_count(match_id)

    return matched_ids

# Main function
def main():
    # Fetch all users from the database
    user_data = fetch_user_data()

    if not user_data:
        print("No user data available.")
        return

    # Create the vector store
    vector_store, ids = create_vector_store(user_data)

    # Example: Current user profile
    current_user_id = 1  # Replace with actual user ID
    current_user = fetch_user_by_id(current_user_id)

    if not current_user:
        print(f"User ID {current_user_id} not found.")
        return

    current_user_profile = generate_user_profile_prompt(current_user)
    print("Current user profile:", current_user_profile)

    # Find similar buddies
    recommendations = find_similar_buddies(current_user_profile, vector_store, ids)
    print("Recommendations (User IDs):", recommendations)

    # Display recommended user profiles
    print("Recommended concert buddies:")
    for rec_id in recommendations:
        recommended_user = fetch_user_by_id(rec_id)
        if recommended_user:
            print(generate_user_profile_prompt(recommended_user))

if __name__ == "__main__":
    main()
