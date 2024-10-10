from flask import Flask, render_template, request, redirect, url_for
import csv
import pandas as pd
import psycopg2
from config import config

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

import secrets
app.secret_key = secrets.token_hex(16)


def get_login(email, password):

    if email == 'STOP':
        return 'TEST FAILURE'
    
    connection = None
    user_info = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email,password))
        user_info = cursor.fetchone() 
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching user info: {error}")
        connection.close()
        return "Database connection error. Please try again later."
    finally:
        if connection:
            connection.close()
    if user_info is not None:
        return True
    else:
        return "Invalid email or password. Please try again."
    

def create_user(username, email, password):
    
    if username == 'STOP':
        return 'User could not be created. Please try again.'
    
    connection = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (username, email, password))
        if cursor.rowcount == 1:
            connection.commit()
            cursor.close()
            return True
        else:
            cursor.close()
            return "User could not be created. Please try again."
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching user info: {error}")
        connection.close()
        return "Database connection error. Please try again later."
    finally:
        if connection:
            connection.close()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        # print(f"Email: {email}, Password: {password}")
        verified_info = get_login(user_email, user_password)
        if verified_info is True:
            # return render_template("test.html", username=None, email=user_email, password=user_password)
            return redirect(url_for('home'))
        else:
            # return render_template("smile.html")
            return render_template("login.html", error=verified_info)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_email = request.form['new_email']
        new_password = request.form['new_password']
        # print(f"Username: {new_username}, Email: {new_email}, Password: {new_password}")
        # created_info = create_user(new_username, new_email, new_password)
        created_info = True
        if created_info is True:
            # return render_template("test.html", username=new_username, email=new_email, password=new_password)
            # return redirect(url_for('home'))
            return redirect(url_for('survey', new_username=new_username, new_email=new_email, new_password=new_password))
        else:
            # return render_template("smile.html")
            return render_template("register.html", error=created_info)
    else:
        return render_template('register.html')
    

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Pass User Data
        new_username = request.args.get('new_username')
        new_email = request.args.get('new_email')
        new_password = request.args.get('new_password')
        # Get Survey Data
        age = request.form['age']
        location = request.form['location']
        genres = request.form.getlist('genre')
        budget = request.form['budget']
        travel_time = request.form['travel_time']

        # Save data to CSV
        with open('temp_survey_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([new_username, new_email, new_password, age, location, ', '.join(genres), budget, travel_time])
        
        return redirect(url_for('home'))
    else:
        return render_template('survey.html')

if __name__ == '__main__':
    app.run(debug=True)