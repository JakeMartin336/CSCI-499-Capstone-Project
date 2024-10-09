from flask import Flask, request, render_template, jsonify, flash
import pandas as pd
import psycopg2
from config import config

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

import secrets
app.secret_key = secrets.token_hex(16)


def get_login(email, password):
    
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
        return 'TEST FAILURE'
    
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
def connect():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        verified_info = get_login(user_email, user_password)
        if verified_info is True:
            # return render_template("test.html", username=None, email=user_email, password=user_password)
            return render_template("smile.html")
            # return redirect(url_for('connect'))
        else:
            # return render_template("smile.html")
            return render_template("index.html", login_error=verified_info)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_email = request.form['new_email']
        new_password = request.form['new_password']
        created_info = create_user(new_username, new_email, new_password)
        if created_info is True:
            # return render_template("test.html", username=new_username, email=new_email, password=new_password)
            return render_template("smile.html")
            # return redirect(url_for('connect'))
        else:
            # return render_template("smile.html")
            return render_template("index.html", register_error=created_info)


if __name__ == '__main__':
    app.run(debug=True)