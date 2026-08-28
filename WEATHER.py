import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# NOTE: don't commit real API keys to GitHub. Better practice is to read this
# from an environment variable, e.g.:
#   import os
#   API_KEY = os.environ.get("OPENWEATHER_API_KEY")
API_KEY = "8b9c9a6e35d550f3937c95fbc6385c12"

# Update these two paths to match wherever the images actually live on your
# machine. Using raw strings (r"...") avoids backslash-escaping issues.
COVER_IMAGE_PATH = r"C:\Users\HomePC\Downloads\istockphoto-477110708-612x612.jpg"
MAIN_IMAGE_PATH = r"C:\Users\HomePC\Downloads\images (2).jpg"

WINDOW_SIZE = "767x547"


def get_weather(city_entry, result_text):
    """Fetch weather data for the city typed into city_entry and update result_text."""
    user_input = city_entry.get().strip()
    if not user_input:
        messagebox.showerror("Error", "Please enter a city name")
        return

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": user_input, "units": "imperial", "APPID": API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not reach the weather service:\n{e}")
        return

    data = response.json()

    # cod can come back as either a string or an int depending on the error type
    if str(data.get("cod")) != "200":
        messagebox.showerror("Error", data.get("message", "No city found"))
        return

    weather = data["weather"][0]["main"]
    temp = data["main"]["temp"]
    coord = data["coord"]
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    country = data["sys"]["country"]

    result_text.set(
        f" Weather Information for {user_input}:\n"
        f" WEATHER: {weather}\n"
        f" TEMPERATURE: {temp}°F\n"
        f" COORDINATE: {coord}\n"
        f" PRESSURE: {pressure}hPa\n"
        f" HUMIDITY: {humidity}%\n"
        f" COUNTRY: {country}"
    )


def build_main_window(root):
    """Populate the main window with its background, widgets, and layout."""
    root.geometry(WINDOW_SIZE)
    root.title("K.H.A.K.E weather app")

    try:
        pil_image = Image.open(MAIN_IMAGE_PATH)
        background_image = ImageTk.PhotoImage(pil_image)
        background_label = tk.Label(root, image=background_image)
        # Keep a reference so Python doesn't garbage-collect the image
        background_label.image = background_image
        background_label.place(relwidth=1, relheight=1)
    except FileNotFoundError:
        print(f"Warning: could not find image at {MAIN_IMAGE_PATH}; skipping background.")

    city_label = tk.Label(
        root, text="Enter city:", font=("Times new roman", 20, "bold"),
        fg="white", bg="midnightblue", width=10
    )
    city_label.pack(pady=(240, 0), padx=5, anchor="center")

    city_entry = tk.Entry(root, font=("Times new roman", 15), width=16)
    city_entry.pack(pady=0, padx=20)

    result_text = tk.StringVar()

    search_button = tk.Button(
        root, text="Get Weather", font=("Times new roman", 15),
        fg="midnightblue", bg="white",
        command=lambda: get_weather(city_entry, result_text)
    )
    search_button.pack(pady=10, padx=10)

    header_label = tk.Label(
        root, text="Weather Information ↓ ↓", font=("arial black", 15, "bold"),
        fg="white", bg="midnightblue", width=36
    )
    header_label.pack(pady=0, padx=10)

    result_label = tk.Label(
        root, textvariable=result_text, font=("arial", 15),
        anchor="center", justify="left", width=46
    )
    result_label.pack(pady=0, padx=10)


def open_main_window(cover_page):
    """Destroy the cover page and open the main window as a new Toplevel."""
    cover_page.destroy()

    main_window = tk.Tk()
    build_main_window(main_window)
    main_window.mainloop()


def build_cover_page():
    cover_page = tk.Tk()
    cover_page.geometry(WINDOW_SIZE)
    cover_page.title("Weather App Cover Page")

    try:
        cover_pil_image = Image.open(COVER_IMAGE_PATH)
        cover_background_image = ImageTk.PhotoImage(cover_pil_image)
        cover_background_label = tk.Label(cover_page, image=cover_background_image)
        cover_background_label.image = cover_background_image
        cover_background_label.place(relwidth=1, relheight=1)
    except FileNotFoundError:
        print(f"Warning: could not find image at {COVER_IMAGE_PATH}; skipping background.")

    cover_label = tk.Label(
        cover_page, text="Welcome to K.H.A.K.E Weather App",
        font=("impact", 25), fg="midnightblue", bg="white"
    )
    cover_label.pack(pady=20)

    open_main_button = tk.Button(
        cover_page, text="OPEN", font=("arial black", 15),
        fg="midnightblue", bg="white",
        command=lambda: open_main_window(cover_page)
    )
    open_main_button.pack(pady=10)

    cover_page.mainloop()


if __name__ == "__main__":
    build_cover_page()