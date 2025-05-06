# This Python program uses the Open-Meteo API to fetch current weather data for a user-specified city, displays it in a Tkinter GUI, 
# and saves the data (including city, weather code, temperature, wind speed, and timestamp) to a CSV file—no API key required.

import requests
import datetime
import csv
import tkinter as tk
from tkinter import messagebox

def get_lat_lon(city_name):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
        response = requests.get(geo_url)
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return result["latitude"], result["longitude"], result["name"]
        else:
            raise Exception("City not found.")
    except Exception as e:
        raise Exception(f"Geocoding error: {e}")

def get_weather_data(city_name):
    try:
        lat, lon, city_resolved = get_lat_lon(city_name)
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        response = requests.get(weather_url)
        data = response.json()
        
        weather = data.get("current_weather", {})
        if not weather:
            return None

        return {
            "city": city_resolved,
            "description": f"Weather code: {weather.get('weathercode')}",
            "temperature": f"{weather.get('temperature')} °C",
            "humidity": "N/A",
            "wind_speed": f"{weather.get('windspeed')} km/h",
            "date": weather.get("time")
        }

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def generate_report(weather_data):
    if weather_data is None:
        return

    with open("weather_report.csv", "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["city", "description", "temperature", "humidity", "wind_speed", "date"])
        writer.writeheader()
        writer.writerow(weather_data)

def fetch_weather():
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    weather = get_weather_data(city)
    if weather:
        result_text.set(
            f"City: {weather['city']}\n"
            f"Description: {weather['description']}\n"
            f"Temperature: {weather['temperature']}\n"
            f"Humidity: {weather['humidity']}\n"
            f"Wind Speed: {weather['wind_speed']}\n"
            f"Date: {weather['date']}"
        )
        generate_report(weather)
        messagebox.showinfo("Success", "Weather data fetched and report saved.")
    else:
        result_text.set("Failed to fetch weather data.")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Weather Report Generator")
root.geometry("400x350")
root.resizable(False, False)

tk.Label(root, text="Enter City Name:", font=("Arial", 12)).pack(pady=10)

city_entry = tk.Entry(root, width=30, font=("Arial", 12))
city_entry.pack()

tk.Button(root, text="Get Weather Report", font=("Arial", 12), command=fetch_weather).pack(pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, font=("Arial", 10), justify="left", wraplength=360).pack(pady=10)

root.mainloop()
