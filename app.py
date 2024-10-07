from flask import Flask, request, render_template
import pandas as pd
import psycopg2
from config import config

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


@app.route("/")
def home():
    # Get user info from FE
    account_id = request.args.get('account_id')
    user_info = None
    
    # Since account_id is a str, convert to int before passing it into function
    if account_id:
        account_id = int(account_id)
        user_info = get_user_info(account_id)

    return render_template("index.html", user=user_info)

if __name__ == "__main__":
    app.run(debug=True)

# @app.route("/mysite")
# def get_user_info():
#     # print(request.args)
#     return "Hello World"