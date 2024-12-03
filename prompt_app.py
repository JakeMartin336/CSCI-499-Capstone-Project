from flask import Flask, render_template, request, jsonify
import numpy as np
import faiss
from supabase import create_client
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Supabase client and OpenAI embeddings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Fetch current authenticated user
def fetch_current_user():
    response = supabase.auth.get_user()
    
    if response.error:
        raise Exception(f"Error fetching current user: {response.error.message}")
    
    return response.data['user']

# Fetch user by ID from Supabase
# def fetch_user_by_id(user_id):
#     response = supabase.table("users").select("*").eq("id", user_id).execute()
    
#     if response.error:
#         raise Exception(f"Error fetching user by ID: {response.error.message}")
    
#     data = response.data
#     return data[0] if data else None

# Generate user profile prompt
def generate_user_profile_prompt(user):
    return (
        f"This is a concert-goer named {user['user_name']}, aged {user['age']}, located in {user['location']}. "
        f"They enjoy {', '.join(user.get('music_genres', [])) or 'No music genres specified'} music, "
        f"have a budget of {user['budget']}, and prefer to travel within {user.get('travel_time', 'No preference')}. "
        f"They have attended concerts like {', '.join(user.get('past_concerts', [])) or 'No past concerts listed'}."
    )

# Create vector store
def create_vector_store(user_data):
    user_embeddings = []
    ids = []

    for user in user_data:
        profile_text = generate_user_profile_prompt(user)
        embedding = embeddings.embed_query(profile_text)
        user_embeddings.append(embedding)
        ids.append(user["id"])

    user_embeddings_np = np.array(user_embeddings, dtype='float32')
    embedding_dim = user_embeddings_np.shape[1]

    index = faiss.IndexFlatL2(embedding_dim)
    index.add(user_embeddings_np)

    return index, ids

# Find similar users
def find_similar_buddies(user_profile_text, vector_store, ids, max_matches=5):
    user_embedding = embeddings.embed_query(user_profile_text)
    distances, indices = vector_store.search(np.array([user_embedding]), max_matches)
    matched_ids = [ids[idx] for idx in indices[0] if idx < len(ids)]
    return matched_ids

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = request.form.get("user_id")

        try:
            # Fetch current user and other data if needed
            current_user = fetch_current_user()

            if not current_user:
                return render_template("prompt.html", error="User not found.")

            # Create vector store based on all users (if needed)
            # Example of fetching all users here, if you want to keep this logic:
            user_data = fetch_current_user() # If needed
            vector_store, ids = create_vector_store(user_data)

            # Generate recommendations
            current_user_profile = generate_user_profile_prompt(current_user)
            recommendations = find_similar_buddies(current_user_profile, vector_store, ids)

            # Fetch recommended user profiles
            recommended_users = [fetch_current_user()(rec_id) for rec_id in recommendations]
            return render_template("prompt.html", recommended_users=recommended_users)
        except Exception as e:
            return render_template("prompt.html", error=str(e))

    return render_template("prompt.html")

if __name__ == "__main__":
    app.run(debug=True)
