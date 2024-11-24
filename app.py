from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from api import get_concerts, example_concerts
import secrets

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
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



if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True)
