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
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.schema import retriever
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize Supabase client
supabase = create_client(url, key)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=openai_key)

# Load data from supabase
def fetch_all_users_as_json():
    # Fetches all users from the Supabase 'users' table and saves to a JSON file.
    try:
        response = supabase.table("users").select("*").execute()
        if response.data:
            with open("users_data.json", "w") as json_file:
                json.dump(response.data, json_file, indent=4)
            print("User data saved to 'users_data.json'")
            return response.data
        else:
            print("No users found.")
            return []
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

# Load current user data as a user text
def get_user_info_as_text(account_id):
    # Fetches a single user's information from Supabase and returns it as JSON.
    try:
        response = supabase.table("users").select("*").eq("id", account_id).execute()
        # print(response)
        if response.data:
            current_user = response.data[0]
            user_text = f"This is a user named {current_user['user_name']} with Age: {current_user['age']}, Location: {current_user['user_location']}, Music Genre: {', '.join(current_user.get('music_genre', [])) or 'No music genre selected'}, Budget: {current_user['budget']}, Travel time: {current_user['travel_time'] or 'Not specified'} | id:{current_user['id']} | matched: {current_user['matched']}"
            return user_text
        else:
            print("No user found with that account_id.")
            return None
    except Exception as error:
        print(f"Error fetching user info: {error}")
        return None
print("This is the current user:", get_user_info_as_text(9))

# Create a vector store for all the users & add them to vector store
def create_vector_store():
    with open("users_data.json", "r") as f:
        user_data = json.load(f)

    user_embeddings = []
    ids = []
    documents = {}

    for i, current_user in enumerate(user_data):
        user_text = f"This is a user named {current_user['user_name']} with Age: {current_user['age']}, Location: {current_user['user_location']}, Music Genre: {', '.join(current_user.get('music_genre') if isinstance(current_user.get('music_genre'), list) else []) or 'No music genre selected'}, Budget: {current_user['budget']}, Travel time: {current_user.get('travel_time', 'Not specified')} | id:{current_user['id']} | matched: {current_user['matched']} "

        # print("User text", user_text)
        user_embedding = embeddings.embed_query(user_text)
        user_embeddings.append(user_embedding)
        user_id = current_user["id"]
        ids.append(user_id)
        
        # Create a document for each user and add to the docstore dictionary
        documents[user_id] = Document(page_content=user_text)

    # Convert the embeddings list to a numpy array
    user_embeddings_np = np.array(user_embeddings, dtype='float32')
    embedding_dim = user_embeddings_np.shape[1]  # Dimension of each embedding

    # Initialize a FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(user_embeddings_np)  # Add embeddings to the FAISS index

    # Initialize the FAISS vector store
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(documents),
        index_to_docstore_id={i: ids[i] for i in range(len(ids))}
    )
    
    print("ID", ids) # show a list of id that were added to vector_store
    return vector_store



# Create an embedding for the current user & find similar users
def find_similar_user(vector_store, current_user_info):
    if isinstance(current_user_info, list):
        current_user_info = " ".join(current_user_info)

    current_user_embedding = embeddings.embed_query(current_user_info)
    results = vector_store.similarity_search_by_vector(
        current_user_embedding,
        k=4 # Returning the top 4 suggestion
    )
    
    return results

vector = create_vector_store()
list_of_rec = find_similar_user(vector, get_user_info_as_text(9))
print("This is the list of rec:", list_of_rec)

# Get the user ID from the document
def get_similar_user_ids(documents):
    user_ids = []
    for doc in documents:
        # Split by the delimiter for the id field and get the user ID
        try:
            _, user_id = doc.page_content.split("| id:")
            user_ids.append(int(user_id.strip()))  # Convert ID to an integer
        except ValueError:
            print(f"Error parsing user ID from document: {doc.page_content}")
    return user_ids
print(get_similar_user_ids(list_of_rec))

# Once we have this infromation we are able to do similar things we did with the regular supabase query and display the information 
# We want to be able to cycle through the people and potentially get variety of people to be recommended
# Trying to incorporate prompt engineering so we can do some sort of RAG (retrieval augemented generation), or some sort of retrieval based on a prompt
# ^ similar to chatgpt