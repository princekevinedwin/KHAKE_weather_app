import threading
import time
import requests
import tkinter as tk
from tkinter import font as tkfont

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# NOTE: don't commit real API keys to GitHub. Better practice is to read this
# from an environment variable, e.g.:
#   import os
#   API_KEY = os.environ.get("OPENWEATHER_API_KEY")
API_KEY = "8b9c9a6e35d550f3937c95fbc6385c12"

WINDOW_W, WINDOW_H = 800, 620

WEATHER_THEMES = {
    "Clear":        {"colors": ("#56CCF2", "#2F80ED"), "icon": "☀️"},
    "Clouds":       {"colors": ("#757F9A", "#D7DDE8"), "icon": "☁️"},
    "Rain":         {"colors": ("#4B6CB7", "#182848"), "icon": "🌧️"},
    "Drizzle":      {"colors": ("#89F7FE", "#66A6FF"), "icon": "🌦️"},
    "Thunderstorm": {"colors": ("#232526", "#414345"), "icon": "⛈️"},
    "Snow":         {"colors": ("#E6DADA", "#607D8B"), "icon": "❄️"},
    "Mist":         {"colors": ("#606C88", "#3F4C6B"), "icon": "🌫️"},
    "Fog":          {"colors": ("#606C88", "#3F4C6B"), "icon": "🌫️"},
    "Haze":         {"colors": ("#606C88", "#3F4C6B"), "icon": "🌫️"},
}
DEFAULT_THEME = {"colors": ("#1E3C72", "#2A5298"), "icon": "🌡️"}
COVER_COLORS = ("#2B5876", "#4E4376")

CARD_COLOR = "#ffffff"
SHADOW_COLOR = "#d4d9e0"
TEXT_DARK = "#1c1c1c"
ACCENT = "#2F80ED"
ACCENT_HOVER = "#1c60c9"
CHIP_COLOR = "#eef1f6"
CHIP_HOVER = "#dfe4ec"


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def hex_to_rgb8(canvas, color):
    r, g, b = canvas.winfo_rgb(color)
    return r >> 8, g >> 8, b >> 8


def draw_gradient(canvas, width, height, color1, color2, tag="gradient"):
    canvas.delete(tag)
    r1, g1, b1 = hex_to_rgb8(canvas, color1)
    r2, g2, b2 = hex_to_rgb8(canvas, color2)
    steps = max(height, 1)
    for i in range(steps):
        nr = int(r1 + (r2 - r1) * (i / steps))
        ng = int(g1 + (g2 - g1) * (i / steps))
        nb = int(b1 + (b2 - b1) * (i / steps))
        color = f"#{nr:02x}{ng:02x}{nb:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags=(tag,))
    canvas.tag_lower(tag)


def round_rect(canvas, x1, y1, x2, y2, radius=24, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def fade_in(window, current=0.0, target=1.0, step=0.08, delay=16):
    current += step
    if current >= target:
        window.attributes("-alpha", target)
        return
    window.attributes("-alpha", current)
    window.after(delay, lambda: fade_in(window, current, target, step, delay))


def add_hover(widget, normal_bg, hover_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------
def build_cover_page():
    cover = tk.Tk()
    cover.title("K.H.A.K.E Weather App")
    cover.geometry(f"{WINDOW_W}x{WINDOW_H}")
    cover.resizable(False, False)
    cover.attributes("-alpha", 0.0)

    canvas = tk.Canvas(cover, width=WINDOW_W, height=WINDOW_H, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    draw_gradient(canvas, WINDOW_W, WINDOW_H, *COVER_COLORS)

    title_font = tkfont.Font(family="Segoe UI", size=34, weight="bold")
    sub_font = tkfont.Font(family="Segoe UI", size=13)

    canvas.create_text(WINDOW_W / 2 + 2, WINDOW_H / 2 - 78, text="K.H.A.K.E",
                        font=title_font, fill="#1a2a3d")
    canvas.create_text(WINDOW_W / 2, WINDOW_H / 2 - 80, text="K.H.A.K.E",
                        font=title_font, fill="white")
    canvas.create_text(WINDOW_W / 2, WINDOW_H / 2 - 35, text="Weather App",
                        font=sub_font, fill="#E8ECF7")
    canvas.create_text(WINDOW_W / 2, WINDOW_H / 2 - 5, text="☀️  🌧️  ⛈️  ❄️  🌫️",
                        font=("Segoe UI Emoji", 22), fill="white")

    open_btn = tk.Button(
        cover, text="OPEN APP", font=("Segoe UI", 14, "bold"),
        fg="white", bg=ACCENT, activebackground=ACCENT_HOVER, activeforeground="white",
        bd=0, padx=30, pady=12, cursor="hand2",
        command=lambda: open_main_window(cover)
    )
    add_hover(open_btn, ACCENT, ACCENT_HOVER)
    canvas.create_window(WINDOW_W / 2, WINDOW_H / 2 + 70, window=open_btn)

    fade_in(cover)
    cover.mainloop()


def open_main_window(cover):
    cover.destroy()
    WeatherApp()


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("K.H.A.K.E Weather App")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.0)

        self.unit = "F"
        self.last_data = None
        self.history = []
        self.spin_angle = 0
        self.spinning = False

        self.canvas = tk.Canvas(self.root, width=WINDOW_W, height=WINDOW_H, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        draw_gradient(self.canvas, WINDOW_W, WINDOW_H, *DEFAULT_THEME["colors"])

        self._build_header()
        self._build_hero()
        self._build_control_card()
        self._build_result_card()

        self._tick_clock()
        fade_in(self.root)
        self.root.mainloop()

    # ---------------- UI builders ----------------
    def _build_header(self):
        self.title_text = self.canvas.create_text(
            30, 30, anchor="w", text="K.H.A.K.E Weather",
            font=("Segoe UI", 18, "bold"), fill="white")
        self.clock_text = self.canvas.create_text(
            WINDOW_W - 30, 30, anchor="e", text="",
            font=("Segoe UI", 12), fill="white")

    def _tick_clock(self):
        self.canvas.itemconfig(self.clock_text, text=time.strftime("%A, %d %b  •  %I:%M:%S %p"))
        self.root.after(1000, self._tick_clock)

    def _build_hero(self):
        self.icon_text = self.canvas.create_text(
            WINDOW_W / 2, 105, text=DEFAULT_THEME["icon"],
            font=("Segoe UI Emoji", 58), fill="white")
        self.city_text = self.canvas.create_text(
            WINDOW_W / 2, 172, text="Search a city",
            font=("Segoe UI", 20, "bold"), fill="white")
        self.temp_text = self.canvas.create_text(
            WINDOW_W / 2, 202, text="",
            font=("Segoe UI", 12), fill="#EAF1FF")

    def _build_control_card(self):
        y1, y2 = 240, 350
        round_rect(self.canvas, 52, y1 + 4, WINDOW_W - 48, y2 + 4, radius=22, fill=SHADOW_COLOR, outline="")
        round_rect(self.canvas, 50, y1, WINDOW_W - 50, y2, radius=22, fill=CARD_COLOR, outline="")

        self.entry_x = WINDOW_W / 2 - 90
        self.entry_y = y1 + 35

        self.city_entry = tk.Entry(
            self.root, font=("Segoe UI", 13), width=22, bd=0,
            highlightthickness=1, highlightbackground="#dcdfe4", highlightcolor=ACCENT)
        self.entry_window = self.canvas.create_window(self.entry_x, self.entry_y, window=self.city_entry)
        self.city_entry.bind("<Return>", lambda e: self.start_search())
        self.city_entry.focus_set()

        self.search_btn = tk.Button(
            self.root, text="Search", font=("Segoe UI", 11, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, activeforeground="white",
            bd=0, padx=14, pady=6, cursor="hand2", command=self.start_search)
        add_hover(self.search_btn, ACCENT, ACCENT_HOVER)
        self.canvas.create_window(WINDOW_W / 2 + 65, self.entry_y, window=self.search_btn)

        self.unit_btn = tk.Button(
            self.root, text="°F / °C", font=("Segoe UI", 10, "bold"),
            bg=CHIP_COLOR, fg=TEXT_DARK, activebackground=CHIP_HOVER,
            bd=0, padx=10, pady=6, cursor="hand2", command=self.toggle_unit)
        add_hover(self.unit_btn, CHIP_COLOR, CHIP_HOVER)
        self.canvas.create_window(WINDOW_W / 2 + 150, self.entry_y, window=self.unit_btn)

        self.status_text = self.canvas.create_text(
            WINDOW_W / 2, y1 + 68, text="", font=("Segoe UI", 10), fill="#888")

        # Loading spinner (hidden until a search starts)
        self.spinner = self.canvas.create_arc(
            WINDOW_W / 2 - 12, y1 + 82, WINDOW_W / 2 + 12, y1 + 106,
            start=0, extent=270, style="arc", width=3, outline=ACCENT, state="hidden")

        # Recent search chips
        self.chips_frame = tk.Frame(self.root, bg=CARD_COLOR)
        self.canvas.create_window(WINDOW_W / 2, y2 - 25, window=self.chips_frame)

    def _build_result_card(self):
        y1, y2 = 370, 590
        round_rect(self.canvas, 52, y1 + 4, WINDOW_W - 48, y2 + 4, radius=22, fill=SHADOW_COLOR, outline="")
        round_rect(self.canvas, 50, y1, WINDOW_W - 50, y2, radius=22, fill=CARD_COLOR, outline="")

        self.empty_text = self.canvas.create_text(
            WINDOW_W / 2, (y1 + y2) / 2, text="Search for a city to see the forecast",
            font=("Segoe UI", 12), fill="#9aa0a8")

        self.detail_labels = {}
        rows = ["Condition", "Wind", "Pressure", "Humidity", "Coordinates", "Country"]
        for i, label in enumerate(rows):
            ly = y1 + 35 + i * 30
            self.canvas.create_text(
                90, ly, anchor="w", text=label, font=("Segoe UI", 11, "bold"),
                fill="#6b7280", tags="detail", state="hidden")
            val_id = self.canvas.create_text(
                WINDOW_W - 90, ly, anchor="e", text="",
                font=("Segoe UI", 11), fill=TEXT_DARK, tags="detail", state="hidden")
            self.detail_labels[label] = val_id

    # ---------------- Behaviour ----------------
    def toggle_unit(self):
        self.unit = "C" if self.unit == "F" else "F"
        if self.last_data:
            self.render_result(self.last_data)

    def start_search(self):
        city = self.city_entry.get().strip()
        if not city:
            self.set_status("Type a city name first", error=True)
            self.shake_entry()
            return
        self.set_status("Fetching weather...", error=False)
        self.start_spinner()
        threading.Thread(target=self._fetch_weather, args=(city,), daemon=True).start()

    def _fetch_weather(self, city):
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "units": "imperial", "APPID": API_KEY}
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.on_error(f"Network error: {e}"))
            return

        if str(data.get("cod")) != "200":
            self.root.after(0, lambda: self.on_error(data.get("message", "City not found")))
            return

        self.root.after(0, lambda: self.on_success(data, city))

    def on_error(self, message):
        self.stop_spinner()
        self.set_status(message, error=True)
        self.shake_entry()

    def on_success(self, data, city):
        self.stop_spinner()
        self.set_status("", error=False)
        self.last_data = data
        self.add_to_history(city)
        self.apply_theme(data["weather"][0]["main"])
        self.render_result(data)

    def apply_theme(self, condition):
        theme = WEATHER_THEMES.get(condition, DEFAULT_THEME)
        draw_gradient(self.canvas, WINDOW_W, WINDOW_H, *theme["colors"])
        self.canvas.itemconfig(self.icon_text, text=theme["icon"])

    def render_result(self, data):
        city_name = data.get("name", "")
        country = data["sys"]["country"]
        temp_f = data["main"]["temp"]
        feels_f = data["main"].get("feels_like", temp_f)

        if self.unit == "F":
            temp, feels, symbol = temp_f, feels_f, "°F"
        else:
            temp, feels, symbol = (temp_f - 32) * 5 / 9, (feels_f - 32) * 5 / 9, "°C"

        self.canvas.itemconfig(self.city_text, text=f"{city_name}, {country}")
        self.canvas.itemconfig(
            self.temp_text, text=f"{round(temp)}{symbol}  •  Feels like {round(feels)}{symbol}")

        self.canvas.itemconfig(self.empty_text, state="hidden")
        self.canvas.itemconfig("detail", state="normal")

        weather = data["weather"][0]["main"]
        wind = data.get("wind", {}).get("speed", "N/A")
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        coord = data["coord"]

        self.canvas.itemconfig(self.detail_labels["Condition"], text=weather)
        self.canvas.itemconfig(self.detail_labels["Wind"], text=f"{wind} mph")
        self.canvas.itemconfig(self.detail_labels["Pressure"], text=f"{pressure} hPa")
        self.canvas.itemconfig(self.detail_labels["Humidity"], text=f"{humidity}%")
        self.canvas.itemconfig(self.detail_labels["Coordinates"], text=f"{coord['lat']}, {coord['lon']}")
        self.canvas.itemconfig(self.detail_labels["Country"], text=country)

    def add_to_history(self, city):
        city_title = city.title()
        if city_title in self.history:
            self.history.remove(city_title)
        self.history.insert(0, city_title)
        self.history = self.history[:5]
        self.refresh_chips()

    def refresh_chips(self):
        for child in self.chips_frame.winfo_children():
            child.destroy()
        for city in self.history:
            chip = tk.Button(
                self.chips_frame, text=city, font=("Segoe UI", 9),
                bg=CHIP_COLOR, fg=TEXT_DARK, bd=0, padx=8, pady=3, cursor="hand2",
                command=lambda c=city: self.quick_search(c))
            add_hover(chip, CHIP_COLOR, CHIP_HOVER)
            chip.pack(side="left", padx=3)

    def quick_search(self, city):
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city)
        self.start_search()

    def set_status(self, message, error=False):
        self.canvas.itemconfig(self.status_text, text=message, fill="#e74c3c" if error else "#888")

    def start_spinner(self):
        self.spinning = True
        self.canvas.itemconfig(self.spinner, state="normal")
        self._animate_spinner()

    def _animate_spinner(self):
        if not self.spinning:
            return
        self.spin_angle = (self.spin_angle + 20) % 360
        self.canvas.itemconfig(self.spinner, start=self.spin_angle)
        self.root.after(40, self._animate_spinner)

    def stop_spinner(self):
        self.spinning = False
        self.canvas.itemconfig(self.spinner, state="hidden")

    def shake_entry(self):
        offsets = [12, -12, 8, -8, 4, 0]

        def step(i=0):
            if i >= len(offsets):
                self.canvas.coords(self.entry_window, self.entry_x, self.entry_y)
                return
            self.canvas.coords(self.entry_window, self.entry_x + offsets[i], self.entry_y)
            self.root.after(35, lambda: step(i + 1))

        step()


if __name__ == "__main__":
    build_cover_page()