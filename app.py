from flask import Flask, render_template, request, jsonify, url_for, redirect, session
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from api import get_concerts

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

import secrets
app.secret_key = secrets.token_hex(16)


def insert_survey(user_id, age, location, genres, budget, travel_time, account_description):
    if account_description == "FAIL ME":
        return "TEST FAILURE OUTPUT"
    
    try:
        insert_survey = (
            supabase.table("users")
            .update({
                "age" : age,
                "account_description" : account_description,
                "user_location" : location,
                "music_genre" : genres,
                "budget" : budget,
                "travel_time" : travel_time,
                "survey_complete" : True
            })
            .eq("id", user_id)
            .execute()
        )
        if insert_survey.data:
            return True
        else:
            return "Error submitting survey. Please try again."
    except Exception as error:
        print(f"Error updating user info: {error}")
        return "Database connection error. Please try again later."


def get_login(email, password):
    if email == 'STOP@STOP':
        return 'TEST FAILURE'
    
    get_login_info = None
    try:
        get_login_info = (
            supabase.table("users")
            .select("*")
            .eq("email_address", email)
            .eq("password", password)
            .execute()
        )
        if get_login_info.data:
            user_id = get_login_info.data[0]['id']
            session['user_id'] = user_id
            if get_login_info.data[0]['survey_complete'] == False:
                return False
            else:
                return True
        else:
            return "Invalid email or password. Please try again."
    except Exception as error:
        print(f"Error fetching user info: {error}")
        return "Database connection error. Please try again later."
    

def create_user(username, email, password):
    if username == 'STOP':
        return 'User could not be created. Please try again.'
    
    create_user = None
    try:
        create_user = (
            supabase.table("users")
            .insert({
                "user_name" : username,
                "email_address" : email,
                "password" : password,
                "survey_complete" : False
            })
            .execute()
        )
        if create_user.data:
            user_id = create_user.data[0]['id']
            session['user_id'] = user_id
            return True
        else:
            return "User could not be created. Please try again."
    except Exception as error:
        print(f"Error fetching user info: {error}")
        return "Database connection error. Please try again later."


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


@app.route('/')
def home():
    # return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        # print(f"Email: {email}, Password: {password}")
        verified_info = get_login(user_email, user_password)
        if verified_info is True:
            # return redirect(url_for('home'))
            # return render_template("smile.html")
            return redirect(url_for('landing'))
        elif verified_info is False:
            return redirect(url_for('survey'))
        else:
            return render_template("login.html", error=verified_info)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')
        # print(f"Username: {new_username}, Email: {new_email}, Password: {new_password}")
        created_info = create_user(new_username, new_email, new_password)
        if created_info is True:
            return redirect(url_for('survey'))
        else:
            return render_template("register.html", error=created_info)
    else:
        return render_template('register.html')
    

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    error = None
    if request.method == 'POST':
        user_id = session.get('user_id') 
        age = request.form['age']
        location = request.form['location']
        genres = request.form.getlist('genre')
        budget = request.form['budget']
        travel_time = request.form['travel_time']
        account_description = request.form['introduction']
        # print([user_id, age, location, ', '.join(genres), budget, travel_time])
        updated_info = insert_survey(user_id, age, location, genres, budget, travel_time, account_description)        
        if updated_info is True:
            # session.pop('user_id', None)
            # return render_template("smile.html")
            return redirect(url_for('landing'))
        else:
            return render_template("survey.html", error=updated_info)
    else:
        return render_template('survey.html')
    

@app.route("/landing")
def landing():
    account_id = session.get('user_id')
    user_info = None
    user_concerts = []
    
    if account_id:
        account_id = int(account_id)
        user_info = get_user_info(account_id)
        user_concerts = get_user_concerts(account_id)

        session['user_info'] = user_info
        session['user_concerts'] = user_concerts

    # For Concert Page
    for genre in user_info['music_genre']:
        get_concerts(genre, user_info['user_location'])



    return render_template("landing.html", user=user_info, concerts=user_concerts)



if __name__ == '__main__':
    app.run(debug=True)