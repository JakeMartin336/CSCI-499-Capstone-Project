import os
import json
import numpy as np
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(url, key)

USER_DATA_FILE = "user_data.json"

def fetch_all_users_as_json():
    # Fetches all users from the Supabase 'users' table and saves to a JSON file.
    try:
        response = supabase.table("users").select("*").execute()
        if response.data:
            # Ensure the directory exists, then create the file if it doesn't exist
            USER_DATA_FILE = "users_data.json"
            # Check if the file exists, if not, it will be created
            with open(USER_DATA_FILE, "w") as json_file:
                json.dump(response.data, json_file, indent=4)
            print(f"User data saved to '{USER_DATA_FILE}'")
            return response.data
        else:
            print("No users found.")
            return []
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []