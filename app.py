from flask import Flask, render_template, request, jsonify, url_for, redirect, session, flash
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import os
import uuid
from werkzeug.utils import secure_filename
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
from datetime import datetime

# Load environment variables
load_dotenv()

# Check if variables are loaded
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

openai_key = os.getenv("OPENAI_API_KEY")
supabase = create_client(url, key)

app = Flask(__name__, static_folder='static')
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)

BUCKET_NAME = "profile-pictures"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

all_concerts = []
socket_users = {}


def insert_friend(user_id, friend_id):
    try:
        response = (
            supabase.table("users")
            .select("contacts")
            .eq("id", user_id)
            .single()
            .execute()
        )
        current_contacts = response.data["contacts"] or []
        if friend_id not in current_contacts:
            current_contacts.append(friend_id)
            update_response = (
                supabase.table("users")
                .update({"contacts": current_contacts})
                .eq("id", user_id)
                .execute()
            )
        
        other_response = (
            supabase.table("users")
            .select("contacts")
            .eq("id", friend_id)
            .single()
            .execute()
        )
        other_current_contacts = other_response.data["contacts"] or []
        if user_id not in other_current_contacts:
            other_current_contacts.append(user_id)
            other_update_response = (
                supabase.table("users")
                .update({"contacts": other_current_contacts})
                .eq("id", friend_id)
                .execute()
            )
        
        return True
    except Exception as error:
        print(f"Error updating contacts: {error}")
        return False


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_friends(user_id):
    try:
        get_friends_ID = (
            supabase.table("users")
            .select("contacts")
            .eq("id", user_id)
            .execute()
        )
        user_contacts = get_friends_ID.data[0]['contacts']
        map_of_friends = {}
        for friend in user_contacts:
            try:
                get_friends_name = (
                    supabase.table("users")
                    .select("user_name")
                    .eq("id", friend)
                    .execute()
                )
                map_of_friends[friend] = get_friends_name.data[0]['user_name']
            except Exception as error:
                print(f"Error fetching user contacts names: {error}")
                return None
        return map_of_friends
    except Exception as error:
        print(f"Error fetching user contacts: {error}")
        return None


def insert_survey(user_id, age, location, genres, budget, travel_time, account_description):
    if account_description == "FAIL ME":
        return "TEST FAILURE OUTPUT"

    try:
        insert_survey = (
            supabase.table("users")
            .update({
                "age": age,
                "account_description": account_description,
                "user_location": location,
                "music_genre": genres,
                "budget": budget,
                "travel_time": travel_time,
                "survey_complete": True
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
            if get_login_info.data[0]['survey_complete'] is False:
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

    try:
        create_user = (
            supabase.table("users")
            .insert({
                "user_name": username,
                "email_address": email,
                "password": password,
                "survey_complete": False
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


def get_user_info(user_id):
    try:
        columns_to_fetch = [
            "id", "created_at", "user_name", "age", "email_address",
            "account_description", "user_location", "music_genre",
            "budget", "travel_time", "contacts", "password", "survey_complete", "profile_picture_url"
        ]

        response = (
            supabase.table("users")
            .select(",".join(columns_to_fetch))
            .eq("id", user_id)
            .execute()
        )

        print("Database Response:", response.data)
        

        if response.data:
            user_info = response.data[0] 
            columns = ["id", "created_at", "user_name", "age", "email_address", "account_description", 
                       "user_location", "music_genre", "budget", "travel_time", "password", "contacts", "survey_complete", "profile_picture_url"]
            user_info = {col: user_info.get(col) for col in columns}
        else:
            print("No user found with that account_id.")
    except Exception as error:
        print(f"Error fetching user info: {error}")
    return user_info


def update_user_info(user_id, updated_data):
    try:
        response = (
            supabase.table("users")
            .update(updated_data)
            .eq("id", user_id)
            .execute()
        )

        print("Update Response:", response.data)

        if response.data and len(response.data) > 0:
            print("User updated successfully:", response.data)
            refreshed_user = get_user_info(user_id)
            print("Refetched User Info:", refreshed_user)
            if refreshed_user:
                return True
            else:
                return "Update succeeded, but failed to retrieve updated data."
        else:
            return "Failed to update user info."
    except Exception as error:
        print(f"Error updating user info: {error}")
        return "Database error."


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
                supabase.table("concerts") \
                    .delete() \
                    .eq("user_id", user_id) \
                    .eq("concert_name", concert_name) \
                    .eq("concert_image", concert_image) \
                    .eq("concert_date", concert_date) \
                    .execute()
            else:
                supabase.table("concerts") \
                    .update({"concert_status": concert_status}) \
                    .eq("user_id", user_id) \
                    .eq("concert_name", concert_name) \
                    .eq("concert_image", concert_image) \
                    .eq("concert_date", concert_date) \
                    .execute()
        else:
            supabase.table("concerts") \
                .insert({
                    "user_id": user_id,
                    "concert_status": concert_status,
                    "concert_name": concert_name,
                    "concert_image": concert_image,
                    "concert_date": concert_date
                }) \
                .execute()
    except Exception as error:
        print(f"Error getting concert info: {error}")


@app.route('/')
def home():
    initialize_app()
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    fetch_all_users_as_json()
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        verified_info = get_login(user_email, user_password)
        if verified_info is True:
            return redirect(url_for('landing'))
        elif verified_info is False:
            return redirect(url_for('survey'))
        else:
            return render_template("login.html", error=verified_info)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')
        created_info = create_user(new_username, new_email, new_password)
        if created_info is True:
            return redirect(url_for('survey'))
        else:
            return render_template("register.html", error=created_info)
    else:
        return render_template('register.html')


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        user_id = session.get('user_id')
        age = request.form['age']
        location = request.form['location']
        genres = request.form.getlist('genre')
        budget = request.form['budget']
        travel_time = request.form['travel_time']
        account_description = request.form['introduction']
        updated_info = insert_survey(user_id, age, location, genres, budget, travel_time, account_description)
        if updated_info is True:
            return redirect(url_for('landing'))
        else:
            return render_template("survey.html", error=updated_info)
    else:
        return render_template('survey.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user_info = get_user_info(user_id)
    success_message, error_message = None, None

   
    avatars = [
        url_for('static', filename='avatars/avatar1.png'),
        url_for('static', filename='avatars/avatar2.png'),
        url_for('static', filename='avatars/avatar3.png'),
        url_for('static', filename='avatars/avatar4.png'),
        url_for('static', filename='avatars/avatar5.png'),
        url_for('static', filename='avatars/avatar6.png'),
        url_for('static', filename='avatars/avatar7.png'),
        url_for('static', filename='avatars/avatar8.png'),
        url_for('static', filename='avatars/avatar9.png'),
        url_for('static', filename='avatars/avatar10.png')
    ]

    if request.method == 'POST':
        chosen_avatar = request.form.get('chosen_avatar')
        if chosen_avatar and chosen_avatar in avatars:
            update_status = update_user_info(user_id, {"profile_picture_url": chosen_avatar})
            if update_status is True:
                user_info['profile_picture_url'] = chosen_avatar
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status
        
        updated_username = request.form.get('username')
        if updated_username and updated_username != user_info['user_name']:
            update_status = update_user_info(user_id, {'user_name': updated_username})
            if update_status is True:
                user_info['user_name'] = updated_username
                if not success_message:
                    success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        # Update user information fields
        updated_username = request.form.get('username')
        if updated_username and updated_username != user_info['user_name']:
            update_status = update_user_info(user_id, {'user_name': updated_username})
            if update_status is True:
                user_info['user_name'] = updated_username
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_email = request.form.get('email')
        if updated_email and updated_email != user_info['email_address']:
            update_status = update_user_info(user_id, {'email_address': updated_email})
            if update_status is True:
                user_info['email_address'] = updated_email
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_age = request.form.get('age')
        if updated_age and updated_age != str(user_info['age']):
            update_status = update_user_info(user_id, {'age': updated_age})
            if update_status is True:
                user_info['age'] = updated_age
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_location = request.form.get('location')
        if updated_location and updated_location != user_info['user_location']:
            update_status = update_user_info(user_id, {'user_location': updated_location})
            if update_status is True:
                user_info['user_location'] = updated_location
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_account_description = request.form.get('account_description')
        if updated_account_description and updated_account_description != user_info['account_description']:
            update_status = update_user_info(user_id, {'account_description': updated_account_description})
            if update_status is True:
                user_info['account_description'] = updated_account_description
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_genres = request.form.getlist('genres')  # Get all selected genres
        if updated_genres and updated_genres != user_info['music_genre']:
            update_status = update_user_info(user_id, {'music_genre': updated_genres})
            if update_status is True:
                user_info['music_genre'] = updated_genres
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_budget = request.form.get('budget')
        if updated_budget and updated_budget != str(user_info['budget']):
            update_status = update_user_info(user_id, {'budget': updated_budget})
            if update_status is True:
                user_info['budget'] = updated_budget
                success_message = "Profile updated successfully!"
            else:
                error_message = update_status

        updated_travel_time = request.form.get('travel_time')
        if updated_travel_time and updated_travel_time != str(user_info['travel_time']):
            update_status = update_user_info(user_id, {'travel_time': updated_travel_time})
            if update_status is True:
                user_info['travel_time'] = updated_travel_time
                success_message = "Profile time updated successfully!"
            else:
                error_message = update_status

        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password and new_password:
            if user_info.get('password') == current_password:
                update_status = update_user_info(user_id, {'password': new_password})
                if update_status is True:
                    user_info['password'] = new_password
                    success_message = "Profile updated successfully!"
                else:
                    error_message = update_status
            else:
                error_message = "Incorrect current password. Please try again."

        updated_travel_time = request.form.get('travel_time')
        if updated_travel_time and updated_travel_time != user_info['travel_time']:
            update_status = update_user_info(user_id, {'travel_time': updated_travel_time})
            if update_status is True:
                user_info['travel_time'] = updated_travel_time
                success_message = "Profile updated successfully!"
            else:
                     error_message = update_status
                
    return render_template("profile.html", user=user_info, success=success_message, error=error_message, avatars=avatars)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            file_data = profile_picture.read()
            # Handle file_data as needed
            return "File uploaded successfully!"
        else:
            return "No file uploaded."
    return render_template('upload.html')


@app.route("/landing")
def landing():
    user_id = session.get('user_id')
    user_info = None
    user_concerts = []

    if user_id:
        user_id = int(user_id)
        user_info = get_user_info(user_id)
        user_concerts = get_user_concerts(user_id)

    session['user_info'] = user_info
    return render_template("landing.html", user=user_info, concerts=user_concerts)


@app.route("/concerts")
def concerts():
    global all_concerts

    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    user_genres = user_info['music_genre']
    user_location = user_info['user_location']

    if len(all_concerts) == 0:
        for genre in user_genres:
            recc_concerts = get_concerts(genre, user_location)
            all_concerts.extend(recc_concerts)

    return render_template("concert.html", all_concerts=all_concerts, )


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
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    attendance = data.get('attendance')
    if attendance not in ['yes', 'no']:
        return jsonify({"error": "Invalid attendance value"}), 400

    concert_name = data.get('concert_name')
    concert_date = data.get('concert_date')
    concert_image = data.get('concert_image')

    if not concert_name or not concert_date or not concert_image:
        return jsonify({"error": "Missing concert details"}), 400

    if attendance == 'yes':
        attendance = 'attended'
        message = f"Concert '{concert_name}' has been marked as {attendance}!"
    elif attendance == 'no':
        attendance = 'DELETE'
        message = f"Concert '{concert_name}' has been deleted!"

    insert_concert(user_id, attendance, concert_name, concert_image, concert_date)
    return jsonify({"message": message})


@app.route('/messages')
def messages():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    username = user_info['user_name']
    friends = get_user_friends(user_id)
    concerts = get_user_concerts(user_id)
    return render_template('messages.html', friends=friends, concerts=concerts, username=username)


@app.route('/add_friend/<user_id>', methods=['POST'])
def friend(user_id):
    try:
        account_id = session.get('user_id')
        if not account_id:
            return jsonify({"error": "User not logged in"}), 401

        newFriendID = int(user_id)
        add_friend = insert_friend(int(account_id), newFriendID)
        
        if add_friend:
            print("Added as friend!", newFriendID)
            return jsonify({"success": True})
        else:
            return jsonify({"error": "User not found"}), 404

    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400


@socketio.on('connect', namespace='/messages')
def handle_connect():
    user_id = int(session.get('user_id'))
    socket_users[user_id] = request.sid
    print(f"UserID: {user_id}, Connected: {request.sid}")


@socketio.on('disconnect', namespace='/messages')
def handle_disconnect():
    user_id = int(session.get('user_id'))
    if user_id in socket_users:
        del socket_users[user_id]
        print(f"User {user_id} disconnected.")


@socketio.on('join', namespace='/messages')
def handle_join(data):
    room = data['room']
    user_id = int(session.get('user_id'))
    username = session.get('user_info')['user_name']
    join_room(room)
    print(f"UserID: {user_id}, Join room: {room}")
    # emit('message', {'msg': f'{username} has entered the room.'}, room=room)


@socketio.on('private_message', namespace='/messages')
def handle_message(data):
    recipient = int(data['recipient'])
    message = data['message']
    sender = session.get('user_info')['user_name']
    if recipient in socket_users:
        emit('private_message', {'sender': sender, 'message': message}, to=socket_users[recipient])
    else:
        emit('private_message', {'sender': 'System', 'message': f"User is offline."}, to=request.sid)



@app.route('/api/user-info/<user_id>', methods=['GET', 'POST'])
def user_info_route(user_id):
    u_info = get_user_info(int(user_id))
    if u_info:
        print("I am user_info", u_info)
        return jsonify(u_info)
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
        print("'users_data.json' already exists.")
        fetch_all_users_as_json()
    setup_faiss_index()


def postgres_changes_callback(payload, *args):
    print("*: ", payload)
    fetch_all_users_as_json()


async def setup_async_realtime_client():
    socket = AsyncRealtimeClient(f"{url}/realtime/v1", key, auto_reconnect=True)
    await socket.connect()

    channel = socket.channel("public:todos")
    await channel.on_postgres_changes("*", callback=postgres_changes_callback).subscribe()
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

    print(f"Parameters received: Venue={venue_name}, Section={section}, Row={row}, Seat={seat}")

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
        print(f"Query response: {response.data}")

        if not response.data:
            return jsonify({'error': 'No images found for the specified criteria.'}), 404
        return jsonify({'image_urls': response.data}), 200
    except Exception as e:
        print(f"Error fetching venue images: {str(e)}")
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

        # Upload image to Supabase storage
        upload_response = supabase.storage.from_('venue-images-bucket').upload(image_filename, image_bytes)
        public_url = supabase.storage.from_('venue-images-bucket').get_public_url(image_filename)

        # Check for duplicate entry
        existing_entry = (
            supabase.table("venue-images")
            .select("*")
            .eq("venue_name", venue_name)
            .eq("section", section)
            .eq("row", row)
            .eq("seat", seat)
            .eq("image_url", public_url)
            .execute()
        )

        if existing_entry.data:
            return jsonify({'error': 'Image already exists for this seat.'}), 400

        # Insert new entry
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
        print(insert_response)
        if not insert_response:
            return jsonify({'error': 'Failed to insert image metadata into database.'}), 500

        return jsonify({'message': 'Venue image added successfully!', 'image_url': public_url}), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f"Failed to upload image: {str(e)}"}), 500


if __name__ == '__main__':
    initialize_app()
    socketio.run(app, host='127.0.0.1', port=5003, debug=True, use_reloader=False)
