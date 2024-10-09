from flask import Flask, request, render_template
import pandas as pd
import psycopg2
from config import config
import json  # Import json for handling JSON requests

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True



def get_user_info(account_id):
    # Fetch user information from the DB
    connection = None
    user_info = None
    try:
        params = config()  # Get DB connection parameters [from my other config file]
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        # Fetch user data with SQL query
        # Make sure account_id is a tuple not just an int (or will get an error)
        cursor.execute("SELECT * FROM users WHERE account_id = %s", (account_id,))
        user_info = cursor.fetchone() 
        print(f"Fetched user info: {user_info}") 

        # If user_info exists, then convert it to a dictionary
        # More info on zip function: https://blog.hubspot.com/website/python-zip#:~:text=The%20%60zip%60%20function%20in%20Python,from%20all%20the%20input%20iterables.
        if user_info:
            columns = ["account_id", "user_name", "age", "email_address", "account_description", "user_location", "music_genre", "budget", "travel_time", "contact_ids"]
            user_info = dict(zip(columns, user_info))

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching user info: {error}")
    finally:
        # Edn connection with DB
        if connection is not None:
            connection.close()
    return user_info


def get_user_concerts(user_id):
    connection = None
    concerts = []
    try:
        params = config()  # Get DB connection parameters
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        # Fetch concerts for the user
        cursor.execute("SELECT concert_id, status FROM user_concerts WHERE user_id = %s", (user_id,))
        concerts = cursor.fetchall()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching user concerts: {error}")
    finally:
        if connection is not None:
            connection.close()
    return concerts


@app.route("/")
def home():
    account_id = request.args.get('account_id')
    user_info = None
    user_concerts = []
    
    if account_id:
        account_id = int(account_id)
        user_info = get_user_info(account_id)
        user_concerts = get_user_concerts(account_id)  # Get concerts for the user

    return render_template("index.html", user=user_info, concerts=user_concerts)

@app.route('/test-db')
def test_db():
    try:
        params = config()  # Get database connection params
        print("Database params:", params)  # Print the database connection parameters
        connection = psycopg2.connect(**params)
        connection.close()
        return "Database connection successful!"
    except Exception as e:
        print(f"Error: {e}")  # Print the error to the console
        return f"Database connection failed: {str(e)}"


@app.route("/api/users/<int:user_id>/interested-concerts", methods=["POST"])
def add_interested_concert(user_id):
    concert_id = request.json.get("concert_id")
    if concert_id is None:
        return {"error": "concert_id is required"}, 400

    connection = None
    try:
        params = config()  # Get DB connection parameters
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO user_concerts (user_id, concert_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, concert_id) DO NOTHING;
        """, (user_id, concert_id))

        connection.commit()
        cursor.close()
        return {"message": "Concert added to interests"}, 201
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding concert: {error}")
        return {"error": "Failed to add concert"}, 500
    finally:
        if connection is not None:
            connection.close()




# ... existing home route ...

if __name__ == "__main__":
    app.run(debug=True)
