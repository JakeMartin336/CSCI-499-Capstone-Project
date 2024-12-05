from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from api import get_concerts, example_concerts
import secrets
from fetch_user import fetch_all_users_as_json
import numpy as np
from faiss_match import recommend_best_match_faiss, setup_faiss_index
import asyncio
import threading
from realtime import AsyncRealtimeClient

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Check if variables are loaded
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

openai_key = os.getenv("OPENAI_API_KEY")
supabase = create_client(url, key)

app = Flask(__name__, static_folder='static')
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)

# Used to keep track of user's that are actively chatting/in a chatting room
rooms = {}

def get_user_friends(user_id):
    user_contacts = None
    try:
        get_friends_ID = (
            supabase.table("users")
            .select("contacts")
            .eq("id", user_id)
            .execute()
        )
        user_contacts = get_friends_ID.data[0]['contacts']
    except Exception as error:
        print(f"Error fetching user contacts: {error}")
        return "Database connection error. Please try again later."
    
    map_of_friends = {}
    for friend in user_contacts:
        try:
            get_friends_name = (
                supabase.table("users")
                .select("user_name")
                .eq("id", friend)
                .execute()
            )
            map_of_friends[friend]=get_friends_name.data[0]['user_name']
        except Exception as error:
            print(f"Error fetching user contacts names: {error}")
            return "Database connection error. Please try again later."
    
    return map_of_friends
    

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
    user_info = None
    try:
        response = supabase.table("users").select("*").eq("id", account_id).execute()
        if response.data:
            user_info = response.data[0] 
            columns = ["id", "created_at", "user_name", "age", "email_address", "account_description", 
                       "user_location", "music_genre", "budget", "travel_time", "contacts"]
            user_info = {col: user_info.get(col) for col in columns}
        else:
            print("No user found with that account_id.")
    except Exception as error:
        print(f"Error fetching user info: {error}")
    
    return user_info


def get_user_concerts(user_id):
    concerts = []
    try:
        response = supabase.table("concerts").select("*").eq("user_id", user_id).execute()
        if response.data:
            concerts = response.data 
        else:
            print(f"Error fetching user concerts: {response.error}")
    except Exception as error:
        print(f"Error fetching user concerts: {error}")
    
    return concerts


def insert_concert(user_id, concert_status, concert_name, concert_image, concert_date):
    try:
        get_concert = (
            supabase.table("concerts")
            .select("*")
            .eq("user_id", user_id)
            .eq("concert_name", concert_name)
            .eq("concert_image", concert_image)
            .eq("concert_date", concert_date)
            .execute()
        )
        if get_concert.data:
            if concert_status == 'DELETE':
                delete_concert = (
                    supabase.table("concerts")
                    .delete()
                    .eq("user_id", user_id)
                    .eq("concert_name", concert_name)
                    .eq("concert_image", concert_image)
                    .eq("concert_date", concert_date)
                    .execute()
                )
            else:
                update_concert = (
                    supabase.table("concerts")
                    .update({
                        "concert_status" : concert_status
                    })
                    .eq("user_id", user_id)
                    .eq("concert_name", concert_name)
                    .eq("concert_image", concert_image)
                    .eq("concert_date", concert_date)
                    .execute()
                )
        else:
            insert_concert = (
                supabase.table("concerts")
                .insert({
                    "user_id": user_id,
                    "concert_status": concert_status,
                    "concert_name": concert_name,
                    "concert_image": concert_image,
                    "concert_date": concert_date
                })
                .execute()
            )
    except Exception as error:
        print(f"Error getting concert info: {error}")
        # return "Database connection error. Please try again later."


@app.route('/')
def home():
    initialize_app()
    # return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    fetch_all_users_as_json()
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
    return render_template("landing.html", user=user_info, concerts=user_concerts)


all_concerts = []
@app.route("/concerts")
def concerts():
    global all_concerts

    user_genres = session.get('user_info')['music_genre']
    user_location = session.get('user_info')['user_location']

    if len(all_concerts) == 0:
        all_concerts = example_concerts()
        # for genre in user_genres:
        #     recc_concerts = get_concerts(genre, user_location)
        #     all_concerts.extend(recc_concerts)
    
    return render_template("concert.html", all_concerts=all_concerts,)


@app.route('/venues')
def venue():
    return render_template('venue.html')


@app.route('/logout')
def logout():
    session.clear()
    global list_index
    list_index = 0
    global all_concerts
    all_concerts = []
    return redirect(url_for('home'))


@app.route('/save_concert', methods=['POST'])
def save_concert():
    data = request.get_json()
    user_id = session.get('user_id')
    status = data.get('status')
    name = data.get('name')
    thumbnail = data.get('thumbnail')
    start_time = data.get('start_time')

    insert_concert(user_id, status, name, thumbnail, start_time)

    return jsonify({"message": f"Concert '{name}' has been marked as {status}!"})


@app.route('/concert_attendance', methods=['POST'])
def concert_attendance():
    user_id = session.get('user_id')

    data = request.get_json()
    attendance = data.get('attendance')
    concert_name = data.get('concert_name')
    concert_date = data.get('concert_date')
    concert_image = data.get('concert_image')
    
    if attendance == 'yes':
        attendance = 'attended'
        message = f"Concert '{concert_name}' has been marked as {attendance}!"
    if attendance == 'no':
        attendance = 'DELETE'
        message = f"Concert '{concert_name}' has been deleted!"

    updated_concert = insert_concert(user_id, attendance, concert_name, concert_image, concert_date)
    
    return jsonify({"message": message})


@app.route('/messages')
def messages():
    account_id = session.get('user_id')
    username = session.get('user_info')['user_name']
    friends = get_user_friends(account_id)
    concerts = get_user_concerts(account_id)
    return render_template('messages.html', friends=friends, concerts=concerts, username=username)





@socketio.on('join')
def on_join(data):
    userID = session.get('user_id')
    friendID = data['friendID']
    
    # room = (userID, friendID)
    room=1

    if not room or not userID or not friendID:
        return

    # Create the room if it doesn't exist
    if room not in rooms:
        rooms[room] = {'users': [userID, friendID], 'messages': []}
    
    # Ensure the user is added to the room
    join_room(room)
    send(f'{userID} has joined the room.', to=room)
    print(f'Room created: {room}')

@socketio.on('leave')
def on_leave(data):
    userID = session.get('user_id')
    friendID = data['friendID']
    
    # room = (userID, friendID)
    room=1

    if room in rooms:
        leave_room(room)
        del rooms[room]  # Remove the room after leaving
        send(f'{userID} has left the room.', to=room)
        print(f'Room removed: {room}')

@socketio.on('message')
def on_message(data):
    userID = session.get('user_id')
    friendID = data['friendID']
    
    # room = (userID, friendID)
    room=1

    if room not in rooms:
        return

    content = {
        "name": userID,
        "message": data["message"]
    }

    # Send the message to the room
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"Message sent to {room}: {content}")


@app.route('/api/user-info/<user_id>', methods=['GET', 'POST'])
def user_info(user_id):
    user_info = get_user_info(int(user_id))
    if user_info:
        print("I am user_info", user_info)
        return jsonify(user_info)  # Respond with user info in json format
    else:
        return jsonify({"error": "User not found"}), 404


def initialize_app():
    print("Initializing app...")
    listener_thread = threading.Thread(target=start_async_realtime_client, daemon=True)
    listener_thread.start()
    
    print("Listening...")
    if not os.path.exists("users_data.json"):
        print("'users_data.json' not found. Creating it...")
        fetch_all_users_as_json()
    else:
        print("'users_data.json' already exists.") # This will load all the users from supabase into a json so we can use them 
        fetch_all_users_as_json()
    setup_faiss_index()

def postgres_changes_callback(payload, *args):
    print("*: ", payload)
    fetch_all_users_as_json()

async def setup_async_realtime_client():
    socket = AsyncRealtimeClient(f"{url}/realtime/v1", key, auto_reconnect=True)
    await socket.connect()

    # Setting up Postgres changes
    channel = socket.channel("public:todos")
    await channel.on_postgres_changes(
        "*", callback=postgres_changes_callback
    ).subscribe()

    # Listen indefinitely
    await socket.listen()

def start_async_realtime_client():
    asyncio.run(setup_async_realtime_client())

@app.route('/api/buddy/recommend', methods=['GET', 'POST'])
def recommend():
    print("Route hit!")
    target_id = session.get('user_id')
    print("Account", target_id)
    if not target_id:
        return jsonify({"error": "target_id parameter is required"}), 400
    
    try:
        target_id = int(target_id)
        matched_user, explanation = recommend_best_match_faiss(target_id)
        print(f"Matched User from recommend_best_match_faiss: {matched_user}")
        print(f"Explanation from recommend_best_match_faiss: {explanation}")
        if matched_user:
            return jsonify({"recommended_user_ids": matched_user}), 200
        else:
            return jsonify({"message": "No suitable match found."}), 404
    except ValueError:
        return jsonify({"error": "Invalid target_id parameter"}), 400



@app.route('/get_venue_images', methods=['GET'])
def get_venue_images():
    venue_name = request.args.get('venue_name')
    section = request.args.get('section')
    row = request.args.get('row')
    seat = request.args.get('seat')
    
    print(f"Parameters received: Venue={venue_name}, Section={section}, Row={row}, Seat={seat}")  # Debug log

    if not venue_name:
        return jsonify({'error': 'Venue name is required.'}), 400

    query = supabase.table("venue-images").select("image_url")
    query = query.eq("venue_name", venue_name)
    
    if section:
        query = query.eq("section", section)
    if row:
        query = query.eq("row", row)
    if seat:
        query = query.eq("seat", seat)
    
    try:
        response = query.execute()
        print(f"Query response: {response.data}")  # Debug log

        if not response.data:
            return jsonify({'message': 'No images found for the specified criteria.'}), 404
        return jsonify({'image_urls': response.data}), 200
    except Exception as e:
        print(f"Error fetching venue images: {str(e)}")  # Debug log
        return jsonify({'error': 'An error occurred while fetching venue images.'}), 500





@app.route('/add_venue_image', methods=['POST'])
def add_venue_image():
    venue_name = request.form.get('venue_name')
    section = request.form.get('section')
    row = request.form.get('row')
    seat = request.form.get('seat')
    image = request.files.get('image')
    
    if not image:
        return jsonify({'error': 'No image file provided.'}), 400

    try:
        image_bytes = image.read()
        image_filename = f"{image.filename}"
        
        upload_response = supabase.storage.from_('venue-images-bucket').upload(image_filename, image_bytes)
        public_url = supabase.storage.from_('venue-images-bucket').get_public_url(image_filename)

        insert_response = (
            supabase.table("venue-images")
            .insert({
                "venue_name": venue_name,
                "section": section,
                "row": row,
                "seat": seat,
                "image_url": public_url,
            })
            .execute()
        )

        if insert_response.get('status_code', 200) != 200:
            return jsonify({'error': 'Failed to insert image metadata into database.'}), 500

        return jsonify({'message': 'Venue image added successfully!', 'image_url': public_url}), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f"Failed to upload image: {str(e)}"}), 500


if __name__ == '__main__':
    # app.run(debug=True)
    initialize_app()
    socketio.run(app, debug=True)
