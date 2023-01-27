from flask import render_template, current_app, url_for, request, redirect, send_file
from datetime import datetime
import requests
import numpy as np
from matplotlib import pyplot as plt


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

def create_plot():
    response = get_response()
    date = datetime.now().strftime("%Y-%m-%d")
    data_set = response["list"]
    space = data_set[0]["dt_txt"].find(" ")
    time_list = []
    temp_list = []
    time_array = ([])
    temp_array = ([])
    for data in data_set:
        time_list.append(data["dt_txt"][space+1:len(data["dt_txt"])-3])
        temp_list.append(convert_kelvin_to_celcius(data["main"]["temp"]))

    time_array = np.array(time_list)
    temp_array = np.array(temp_list)

    plt.figure()
    plt.bar(time_array,temp_array)
    plt.savefig("current_plot.png")

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