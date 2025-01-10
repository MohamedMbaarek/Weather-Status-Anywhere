from flask import render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import Database
import requests
from psycopg2.extras import RealDictCursor
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime, timedelta


def convert_kelvin_to_celcius(kelvin):
	return int(kelvin - 273.15)

def convert_wind_speed(speed):
	return format((speed * 3600)/1000,".2f")


def get_response(city):
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    API_Key = open("API_Key.txt","r").read()
    CITY = city
    url = BASE_URL + "q=" + CITY + "&appid=" + API_Key
    response = requests.get(url).json()

    return response


def create_plot(cityName):
    response = get_response(cityName)
    date = datetime.now().strftime("%Y-%m-%d")
    data_set = response["list"]
    space = data_set[0]["dt_txt"].find(" ")
    time_list = []
    temp_list = []

    for data in data_set:
        time_list.append(data["dt_txt"][space + 1:len(data["dt_txt"]) - 3])
        temp_list.append(convert_kelvin_to_celcius(data["main"]["temp"]))

    time_array = np.array(time_list)
    temp_array = np.array(temp_list)

    plt.figure(figsize=(10, 8))
    plt.bar(time_array, temp_array, color='#F28B30', alpha=0.8, edgecolor='#732F20')

    plt.gca().set_facecolor((0, 0, 0, 0))
    plt.gcf().set_facecolor((1, 1, 1, 0))

    plt.title("Temperature Forecast", fontsize=16, color='Black')
    plt.xlabel("Time", fontsize=12, color='Black')
    plt.ylabel("Temperature (°C)", fontsize=12, color='Black')
    plt.xticks(rotation=45, fontsize=10, color='Black')
    plt.yticks(fontsize=10, color='Black')
    plt.tight_layout()

    plt.savefig("static/current_plot.png", transparent=True)
    plt.close()

def create_plot_precipitation(cityName):
    response = get_response(cityName)
    data_set = response["list"]
    
    precipitation_list = []
    time_list = []

    for entry in data_set:
        time = entry["dt_txt"].split(" ")[1][:-3]
        time_list.append(time)

        if "rain" in entry and "3h" in entry["rain"]:
            precipitation_list.append(entry["rain"]["3h"])
        else:
            precipitation_list.append(entry["main"]["humidity"])

    time_array = np.array(time_list)
    data_array = np.array(precipitation_list)

    data_type = "Precipitation (mm)" if "rain" in data_set[0] else "Humidity (%)"

    plt.figure(figsize=(10, 8))
    plt.bar(time_array, data_array, color='#30A2DA', alpha=0.8, edgecolor='#005288')

    plt.gca().set_facecolor((0, 0, 0, 0))
    plt.gcf().set_facecolor((1, 1, 1, 0))
    
    plt.title(f"{data_type} Forecast", fontsize=16, color='Black')
    plt.xlabel("Time", fontsize=12, color='Black')
    plt.ylabel(data_type, fontsize=12, color='Black')
    plt.xticks(rotation=45, fontsize=10, color='Black')
    plt.yticks(fontsize=10, color='Black')
    plt.tight_layout()

    plt.savefig("static/precipitation_plot.png", transparent=True)
    plt.close()


def login_page():
    if "user" in session:
        return redirect(url_for("home_page"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Both fields are required."
            return render_template("login.html", title="Sign in", error=error)

        conn = Database.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.permanent = True
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
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password or not confirm_password:
            error = "All fields are required."
            return render_template("register.html", title="Register", error=error)

        if password != confirm_password:
            error = "Passwords do not match."
            return render_template("register.html", title="Register", error=error)

        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            error = "Username or email is already taken."
            return render_template("register.html", title="Register", error=error)

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("login_page"))

    return render_template("register.html", title="Register")


def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

def forecast():
    cityName = request.args["cityName"]
    response = get_response(cityName)
    temp = convert_kelvin_to_celcius(response["list"][0]["main"]["temp"])
    hum = response["list"][0]["main"]["humidity"]
    temp_min = convert_kelvin_to_celcius(response["list"][0]["main"]["temp_min"])
    temp_max = convert_kelvin_to_celcius(response["list"][0]["main"]["temp_max"])
    wind_speed = convert_wind_speed(response["list"][0]["wind"]["speed"]) 
    desc = response["list"][0]["weather"][0]["description"]
    city = response["city"]["name"]
    icon_id ="http://openweathermap.org/img/wn/" + response["list"][0]["weather"][0]["icon"] + "@2x.png"


    date_time = datetime.now().strftime("%I:%M %p, %a, %b %d, %Y")

    create_plot(cityName)
    create_plot_precipitation(cityName)

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

def home_page():
    if request.method=="GET":
        return render_template("home.html", title="Home")
    else:
        cityName = request.form.get("search")
        response = get_response(cityName)
        if response['cod'] == "404":
            error = cityName + " is not a valid city name"
            return render_template("home.html", title="Home", error=error)
        
        return redirect(url_for("forecast",cityName=cityName))