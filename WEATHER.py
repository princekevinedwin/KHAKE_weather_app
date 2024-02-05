import requests
from tkinter import messagebox


def get_weather():
    global city_entry, result_text

    user_input = city_entry.get()

    api_key = "8b9c9a6e35d550f3937c95fbc6385c12"
    weather_data = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={user_input}&units=imperial&APPID={api_key}"
    )

    if weather_data.json()["cod"] == "404":
        messagebox.showerror("Error", "No city found")
    else:
        weather = weather_data.json()["weather"][0]["main"]
        temp = weather_data.json()["main"]["temp"]
        coord = weather_data.json()["coord"]
        pressure = weather_data.json()["main"]["pressure"]
        humidity = weather_data.json()["main"]["humidity"]
        sys = weather_data.json()["sys"]["country"]

        header_text = f"Weather Information for {user_input}:"

        result_text.set(
            f" {header_text}\n WEATHER: {weather}\n TEMPERATURE: {temp}°F\n COORDINATE: {coord}\n PRESSURE: {pressure}hPa\n HUMIDITY: {humidity}%\n COUNTRY: {sys}")


