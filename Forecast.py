from datetime import datetime

class Forecast:
    def __init__(self, temp, humidity, temp_max, temp_min, wind, desc):
        self.temp = temp
        self.humidity = humidity
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.wind = wind 
        self.desc = desc

    def get_temp():
        return self.temp

    def get_humidity():
        return self.humidity

    def get_temp_max():
        return self.temp_max

    def get_temp_min():
        return self.temp_min

    def get_wind():
        return self.wind

    def get_desc():
        return self.desc