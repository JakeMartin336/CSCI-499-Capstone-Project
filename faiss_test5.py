import os
import json
import numpy as np
import faiss
from dotenv import load_dotenv
from uuid import uuid4
from supabase import create_client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize Supabase client
supabase = create_client(url, key)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=openai_key)

# Path to store the recommendation count
RECOMMENDATION_COUNT_FILE = "recommendation_count.json"

# Recommendation Count Management
def load_recommendation_count():
    # Load the recommendation count from a JSON file.
    if os.path.exists(RECOMMENDATION_COUNT_FILE):
        with open(RECOMMENDATION_COUNT_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding {RECOMMENDATION_COUNT_FILE}. Initializing with empty count.")
                return {}
    else:
        return {}

def save_recommendation_count(count_dict):
    with open(RECOMMENDATION_COUNT_FILE, "w") as file:
        json.dump(count_dict, file, indent=4)

def initialize_recommendation_count():
    # Fetch users from JSON file and initialize their recommendation count as 0 (not matched yet)
    with open("users_data.json", "r") as f:
        user_data = json.load(f)
    
    for user in user_data:
        user_id = str(user['id'])
        if user_id not in recommendation_count:
            recommendation_count[user_id] = 0
    
    save_recommendation_count(recommendation_count)
    print("Recommendation count initialized:", recommendation_count)

recommendation_count = load_recommendation_count()

# Initialize vector store
def create_vector_store():
    with open("users_data.json", "r") as f:
        user_data = json.load(f)

    user_embeddings = []
    ids = []
    documents = {}

    for current_user in user_data:
        user_text = f"This is a user named {current_user['user_name']} with Age: {current_user['age']}, Location: {current_user['user_location']}, Music Genre: {', '.join(current_user.get('music_genre') if isinstance(current_user.get('music_genre'), list) else []) or 'No music genre selected'}, Budget: {current_user['budget']}, Travel time: {current_user['travel_time'] or 'Not specified'} | id:{current_user['id']}"
        
        # Create embeddings
        user_embedding = embeddings.embed_query(user_text)
        user_embeddings.append(user_embedding)
        user_id = current_user["id"]
        ids.append(user_id)
        
        # Create a document for each user and add to the docstore dictionary
        documents[user_id] = Document(page_content=user_text)

    user_embeddings_np = np.array(user_embeddings, dtype='float32')
    embedding_dim = user_embeddings_np.shape[1]

    # Initialize FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(user_embeddings_np)

    # Initialize the FAISS vector store
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(documents),
        index_to_docstore_id={i: ids[i] for i in range(len(ids))}
    )

    print("ID list initialized in vector store:", ids)
    return vector_store

# Recommendation Functionality
def find_similar_user(vector_store, current_user_info, max_matches=4):
    """Find users similar to the current user based on embeddings and recommendation count."""
    if isinstance(current_user_info, list):
        current_user_info = " ".join(current_user_info)

    # Generate the current user's embedding
    current_user_embedding = embeddings.embed_query(current_user_info)
    
    # Retrieve initial candidates from the vector store
    results = vector_store.similarity_search_by_vector(
        current_user_embedding,
        k=max_matches * 2 
    )
    
    # Sort results based on the current recommendation count (lower = more matching)
    results = sorted(
        results,
        key=lambda doc: recommendation_count.get(doc.page_content.split("| id:")[1].strip(), 0)
    )
    
    # Select the top users with the least recommendation count
    selected_users = results[:max_matches]
    
    # Update the recommendation count for each selected user
    for user in selected_users:
        user_id = user.page_content.split("| id:")[1].strip()
        recommendation_count[user_id] += 1
    
    # Save the updated recommendation counts to the file
    save_recommendation_count(recommendation_count)
    
    return selected_users

# User Info Management
def get_user_info_as_text(user_id):
    with open("users_data.json", "r") as f:
        user_data = json.load(f)
    
    # Find user by ID and format user info
    for user in user_data:
        if user["id"] == user_id:
            return f"User {user['user_name']} - Age: {user['age']}, Location: {user['user_location']}, Music Genre: {', '.join(user.get('music_genre') if isinstance(user.get('music_genre'), list) else []) or 'No music genre selected'}, Budget: {user['budget']}, Travel time: {user['travel_time'] or 'Not specified'}"
    
    return "User not found."

def main():
    # Initialize recommendation count
    initialize_recommendation_count()

    # Create the vector store for all users
    vector_store = create_vector_store()

    current_user_text = get_user_info_as_text(9)
    print("This is the current user:", current_user_text)

    # Find similar users with filtering
    list_of_rec = find_similar_user(vector_store, current_user_text)
    print("This is the list of recommendations:", list_of_rec)

    # Extract user IDs from recommendations
    recommended_user_ids = [user.page_content.split("| id:")[1].strip() for user in list_of_rec]
    print("Recommended user IDs:", recommended_user_ids)

if __name__ == "__main__":
    main()



