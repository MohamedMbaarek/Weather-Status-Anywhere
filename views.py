from flask import render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import Database
import requests
import numpy as np
from matplotlib import pyplot as plt
from psycopg2.extras import RealDictCursor


def convert_kelvin_to_celcius(kelvin):
	return int(kelvin - 273.15)

def convert_wind_speed(speed):
	return format((speed * 3600)/1000,".2f")


def get_response():
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    API_Key = open("API_Key.txt","r").read()
    CITY = request.form['search']
    url = BASE_URL + "q=" + CITY + "&appid=" + API_Key
    response = requests.get(url).json()

    return response

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def create_plot():
    response = get_response()  # Replace with your API call
    date = datetime.now().strftime("%Y-%m-%d")
    data_set = response["list"]
    space = data_set[0]["dt_txt"].find(" ")
    time_list = []
    temp_list = []

    for data in data_set:
        time_list.append(data["dt_txt"][space + 1:len(data["dt_txt"]) - 3])
        temp_list.append(convert_kelvin_to_celcius(data["main"]["temp"]))

    # Convert to numpy arrays for plotting
    time_array = np.array(time_list)
    temp_array = np.array(temp_list)

    # Plot customization
    plt.figure(figsize=(10, 6))
    plt.bar(time_array, temp_array, color='#F28B30', alpha=0.8, edgecolor='#732F20')

    # Styling the plot to match the transparent form style
    plt.gca().set_facecolor((0, 0, 0, 0))  # Transparent background for plot area
    plt.gcf().set_facecolor((1, 1, 1, 0))  # Transparent overall background

    plt.title("Temperature Forecast", fontsize=16, color='white')
    plt.xlabel("Time", fontsize=12, color='white')
    plt.ylabel("Temperature (°C)", fontsize=12, color='white')
    plt.xticks(rotation=45, fontsize=10, color='white')
    plt.yticks(fontsize=10, color='white')
    plt.tight_layout()

    # Save the plot as a transparent PNG
    plt.savefig("static/current_plot.png", transparent=True)
    plt.close()


def login_page():
    # If user is already logged in, redirect to home page
    if "user" in session:
        return redirect(url_for("home_page"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if both fields are provided
        if not username or not password:
            error = "Both fields are required."
            return render_template("login.html", title="Sign in", error=error)

        # Get a database connection
        conn = Database.get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for fetching results as dictionaries

        # Query to fetch user details by username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):  # Check if user exists and password is correct
            session["user"] = user["username"]
            return redirect(url_for("home_page"))
        else:
            error = "Invalid username or password."
            return render_template("login.html", title="Sign in", error=error)

    return render_template("login.html", title="Sign in")

def register_page():
    if "user" in session:
        return redirect(url_for("home_page"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            error = "All fields are required."
            return render_template("register.html", title="Register", error=error)

        conn = Database.get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            error = "Username or email is already taken."
            return render_template("register.html", title="Register", error=error)

        # Save the new user to the database
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        # Log the user in after registration
        #session["user"] = username
        return redirect(url_for("login_page"))

    return render_template("register.html", title="Register")



def home_page():
    if request.method=="GET":
        return render_template("home.html", title="Home")
    else:
        response = get_response()
        if response['cod'] == "404":
            error = request.form.get("search") + " is not a valid city name"
            return render_template("home.html", title="Home", error=error)

        temp = convert_kelvin_to_celcius(response["list"][0]["main"]["temp"])
        hum = response["list"][0]["main"]["humidity"]
        temp_min = convert_kelvin_to_celcius(response["list"][0]["main"]["temp_min"])
        temp_max = convert_kelvin_to_celcius(response["list"][0]["main"]["temp_max"])
        wind_speed = convert_wind_speed(response["list"][0]["wind"]["speed"]) 
        desc = response["list"][0]["weather"][0]["description"]
        city = response["city"]["name"]
        icon_id ="http://openweathermap.org/img/wn/" + response["list"][0]["weather"][0]["icon"] + "@2x.png"


        date_time = datetime.now().strftime("%I:%M %p, %a, %b %d, %Y")

        create_plot()

        return render_template("Forecast.html",title="Weather Forecast", 
            temperature=temp, 
            time=date_time, 
            city=city,
            humidity=hum,
            max_temp=temp_max,
            min_temp=temp_min,
            wind=wind_speed,
            description=desc,
            icon=icon_id)