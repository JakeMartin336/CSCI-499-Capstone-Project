from flask import Flask, request, render_template
import pandas as pd
import psycopg2
from config import config
import json 
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

# Connect to supabase using the information from SUPABASE
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

def get_user_info(account_id):
    # Get user information from the Supabase "users" table
    user_info = None
    try:
        # Use `select` to retrieve the columns where id == account_id(`eq` to filter by `id`)
        response = supabase.table("users").select("*").eq("id", account_id).execute()
        
        # Check if data exists in the response
        if response.data:
            user_info = response.data[0] 

            # Convert response to dictionary with preferred column names, if necessary
            columns = ["account_id", "created_at", "user_name", "age", "email_address", "account_description", 
                       "user_location", "music_genre", "budget", "travel_time", "contact_ids"]
            user_info = {col: user_info.get(col) for col in columns}  # Ensures consistent keys
            print(f"Fetched user info: {user_info}")
        else:
            print("No user found with that account_id.")
    
    except Exception as error:
        print(f"Error fetching user info: {error}")
    
    return user_info


def get_user_concerts(user_id):
    concerts = []
    try:
        # Get user concerts from the supabase 'user_concert' DB, where the id is user_id
        response = supabase.table("user_concerts").select("concert_id, status").eq("id", user_id).execute()
        if response.status_code == 200:
            concerts = response.data 
        else:
            print(f"Error fetching user concerts: {response.error}")
    except Exception as error:
        print(f"Error fetching user concerts: {error}")

    return concerts

# This is the landing page route
@app.route("/")
def home():
    account_id = request.args.get('account_id')
    user_info = None
    user_concerts = []
    
    if account_id:
        account_id = int(account_id)
        user_info = get_user_info(account_id)
        user_concerts = get_user_concerts(account_id)

    return render_template("index.html", user=user_info, concerts=user_concerts)

# Making a simple query to test for connection
@app.route('/test-db')
def test_db():
    try:
        response = supabase.from_("users").select("*").limit(1).execute()

        if response.status_code == 200:
            return "Database connection successful!"
        else:
            return f"Database connection failed: {response.error}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Database connection failed: {str(e)}"

# Route to get the interested concerts that the user favorited
@app.route("/api/users/<int:user_id>/interested-concerts", methods=["POST"])
def add_interested_concert(user_id):
    concert_id = request.json.get("concert_id")
    if concert_id is None:
        return {"error": "concert_id is required"}, 400
    try:
        # Get the concert information from the supabase 'user_concerts' table
        response = supabase.table("user_concerts").insert({
            "id": user_id,
            "concert_id": concert_id
        }).execute()

        if response.status_code == 201:
            return {"message": "Concert added to interests"}, 201
        else:
            print(f"Error adding concert: {response.error}")
            return {"error": "Failed to add concert"}, 500
    except Exception as error:
        print(f"Error adding concert: {error}")
        return {"error": "Failed to add concert"}, 500

# ... existing home route ...

if __name__ == "__main__":
    app.run(debug=True)
