import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Make city_entry and result_text global variables
city_entry = None
result_text = None


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


def open_main_window():
    global city_entry, result_text
    cover_page.destroy()
    main_window = tk.Tk()
    main_window.geometry("767x547")
    main_window.title("K.H.A.K.E weather app")

    # Pillow
    image_path = r"C:\Users\user pc\Pictures\Screenshot 2024-01-28 235308.png"
    pil_image = Image.open(image_path)
    background_image = ImageTk.PhotoImage(pil_image)

    background_label = tk.Label(main_window, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    # Widgets
    city_label = tk.Label(main_window, text="Enter city:", font=("Times new roman", 20, "bold"), fg="white",
                          bg="midnightblue", width=10)
    city_label.pack(pady=(240, 0), padx=5, anchor='center')

    city_entry = tk.Entry(main_window, font=("Times new roman", 15), width=16)
    city_entry.pack(pady=0, padx=20)

    search_button = tk.Button(main_window, text="Get Weather", command=get_weather, font=("Times new roman", 15),
                              fg="midnightblue", bg="white")
    search_button.pack(pady=10, padx=10)

    header_label = tk.Label(main_window, text="Weather Information ↓ ↓", font=("arial black", 15, "bold"), fg="white",
                            bg="midnightblue", width=36)
    header_label.pack(pady=0, padx=10)

    result_text = tk.StringVar()
    result_label = tk.Label(main_window, textvariable=result_text, font=("arial", 15), anchor="center", justify="left",
                            width=46)
    result_label.pack(pady=0, padx=10)

    main_window.mainloop()


# Cover page
cover_page = tk.Tk()
cover_page.geometry("767x547")
cover_page.title("Weather App Cover Page")

# Pillow for cover page
cover_image_path = r"C:\Users\user pc\Pictures\853710_weather-wallpapers-free-desktop-backgrounds-wallpapers" \
                   r"-path_1920x1200_h.jpg"
cover_pil_image = Image.open(cover_image_path)
cover_background_image = ImageTk.PhotoImage(cover_pil_image)

cover_background_label = tk.Label(cover_page, image=cover_background_image)
cover_background_label.place(relwidth=1, relheight=1)

cover_label = tk.Label(cover_page, text="Welcome to K.H.A.K.E Weather App", font=("impact", 25), fg="midnightblue",
                       bg="white")
cover_label.pack(pady=20)

# Button to open the main window
open_main_button = tk.Button(cover_page, text="OPEN", command=open_main_window, font=("arial black", 15),
                             fg="midnightblue", bg="white")
open_main_button.pack(pady=10)

cover_page.mainloop()
