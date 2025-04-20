import requests
import urllib
import os
import dotenv
from utils import *
import math

route_url = "https://graphhopper.com/api/1/route?"

dotenv.load_dotenv()
graphhopper_api_key = os.getenv("GH_API_KEY")
genai_api_key = os.getenv("GEMINI_API_KEY")

# Validate API keys
if not graphhopper_api_key:
    print("❌ Error: Graphhopper API key (GH_API_KEY) is not set.")
    exit(1)
if not genai_api_key:
    print("❌ Error: Gemini API key (GEMINI_API_KEY) is not set.")
    exit(1)

genai_model = "gemini-2.0-flash"

geo = Geocoding(graphhopper_api_key)
gpt = Genai(genai_api_key, genai_model)


import requests
import os

import requests

class OpenMeteo:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, lat, lng, hours=12):
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}"
            f"&hourly=temperature_2m,weathercode,wind_speed_10m&timezone=auto"
        )
        response = requests.get(url)
        data = response.json()
        if (hours > 168):
            print("The travel duration exceeds the available forecast range.\n Weather conditions will be shown for up to the next 168 hours only.")

        hourly = data.get("hourly", {})
        available_hours = len(hourly.get("time", []))
        #print(f" Available forecast hours: {available_hours}")  # Debug

        hours = min(hours, available_hours)  # cap to prevent out-of-range

        try:
            forecast = [
                f"{hourly['time'][i]}: {hourly['temperature_2m'][i]}°C, "
                f"{self.decode_weather(hourly['weathercode'][i])}, "
                f"wind {hourly['wind_speed_10m'][i]} km/h"
                for i in range(hours)
            ]
            return "\n".join(forecast)
        except Exception as e:
            return f"❌ Error parsing weather data: {str(e)}"



    def decode_weather(self, code):
        # Simple mapping for extreme conditions
        weather_map = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "fog", 48: "depositing rime fog",
            51: "light drizzle", 61: "light rain", 71: "light snow",
            95: "thunderstorm", 96: "thunderstorm w/ hail"
        }
        return weather_map.get(code, "unknown")



def check_quit(user_input):
    if user_input == "quit" or user_input == "q":
        return True
    else:
        return False

def print_steps(data, orig, dest):
    distance_m = data["paths"][0]["distance"]
    duration_ms = data["paths"][0]["time"]

    miles = distance_m / 1000 / 1.61
    km = distance_m / 1000

    sec = int(duration_ms / 1000 % 60)
    minutes = int(duration_ms / 1000 / 60 % 60)
    hours = int(duration_ms / 1000 / 60 / 60)

    print("📏 Distance Traveled: {:.1f} miles / {:.1f} km".format(miles, km))
    print("⏱️ Trip Duration: {:02d}:{:02d}:{:02d}".format(hours, minutes, sec))
    print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

    try:
        summary = gpt.generate_route_summary(data, orig, dest, vehicle)
        print("🤖 AI Route Summary:")
        print(f"💬 {summary}")
        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
    except Exception as e:
        print(f"⚠️ Couldn't generate route summary: {str(e)}")

    for step in data["paths"][0]["instructions"]:
        path_text = step["text"]
        direction_arrow = "➡️"  # default is right

        path_text_lower = path_text.lower()
        if "left" in path_text_lower:
            direction_arrow = "⬅️"
        elif "right" in path_text_lower:
            direction_arrow = "➡️"
        elif "straight" in path_text_lower or "continue" in path_text_lower:
            direction_arrow = "⬆️"
        elif "u-turn" in path_text_lower or "turnaround" in path_text_lower:
            direction_arrow = "🔄"
        elif "arrive" in path_text_lower or "destination" in path_text_lower:
            direction_arrow = "🏁"
        elif "depart" in path_text_lower or "start" in path_text_lower:
            direction_arrow = "🚩"
        elif "roundabout" in path_text_lower or "rotary" in path_text_lower:
            direction_arrow = "🔄"
        elif "slight left" in path_text_lower:
            direction_arrow = "↖️"
        elif "slight right" in path_text_lower:
            direction_arrow = "↗️"
        elif "sharp left" in path_text_lower:
            direction_arrow = "↩️"
        elif "sharp right" in path_text_lower:
            direction_arrow = "↪️"

        if "distance" in step:
            step_distance = step["distance"]
            # Format distance in a more readable way
            if step_distance < 100:
                distance_str = f"{step_distance:.0f} m"
            else:
                distance_str = f"{step_distance / 1000:.1f} km / {step_distance / 1000 / 1.61:.1f} miles"
            print(f"{direction_arrow}     {path_text} ({distance_str})")
        else:
            print(f"{direction_arrow}     {path_text}")



while True:
    print("🚗 Vehicle profiles available on Graphhopper: 🚗")
    print("🚗 car, 🚲 bike, 🚶 foot, 🚌 public")
    profile = ["car", "bike", "foot", "public"]
    vehicle = input("🔍 Enter a vehicle profile from the list above: ").strip().lower()

    if check_quit(vehicle):
        break
    elif vehicle not in profile:
        vehicle = "car"
        print("⚠️ No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("🏁 Starting Location: ")
    if check_quit(loc1):
        break
    orig_status, orig_lat, orig_lng, orig_loc = geo.geocoding(loc1)

    loc2 = input("🏁 Destination: ")
    if check_quit(loc2):
        break
    dest_status, dest_lat, dest_lng, dest_loc = geo.geocoding(loc2)

    print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

    paths_status = 404
    paths_data = None
    if vehicle == "public":
        try:
            start_time = input("🏁 Please provide a start time (e.g. 1pm): ")
            if check_quit(start_time):
                break
            paths_data, paths_status = gpt.route_public_transportation(orig_loc, dest_loc, start_time)
        except Exception as e:
            print(f"⚠️ Couldn't generate route summary: {str(e)}")

    elif orig_status == 200 and dest_status == 200:
        op = "&point=" + str(orig_lat) + "%2C" + str(orig_lng)
        dp = "&point=" + str(dest_lat) + "%2C" + str(dest_lng)
        paths_url = route_url + urllib.parse.urlencode(
            {"key": graphhopper_api_key, "vehicle": vehicle}
        ) + op + dp

        response = requests.get(paths_url)
        paths_status = response.status_code
        paths_data = response.json()

        print("🛣️ Routing API Status: " + str(paths_status))
        print("🔗 Routing API URL:\n" + paths_url)
        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

        icon = "🚗" if vehicle == "car" else "🚲" if vehicle == "bike" else "🚶"
        print(
            f"🧭 Directions from {orig_loc} to {dest_loc} by {icon} {vehicle}"
        )
        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

    if paths_status == 200 and paths_data is not None:
        print_steps(paths_data, orig_loc, dest_loc)
        
        travel_time = paths_data["paths"][0]["time"]
        travel_time_in_hour = float(travel_time) /1000/ 60/ 60



        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

        weather = OpenMeteo()
        curr_weather = weather.get_weather(orig_lat, orig_lng, hours= 1)
        forecast = weather.get_weather(dest_lat, dest_lng, hours=math.ceil(travel_time_in_hour))

        weather_advisory = gpt.check_weather_conditions(orig_loc, dest_loc, str(travel_time_in_hour), curr_weather, forecast)
        print("🌦️ Weather Advisory:")
        print(weather_advisory)






        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

        voice_option = input("Would you like voice-like instructions? (y/n): ").lower()
        if check_quit(voice_option):
            break
        if voice_option.startswith('y'):
            natural_instructions = gpt.convert_to_natural_instructions(paths_data["paths"][0]["instructions"])
            voice_navigation(natural_instructions)

        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
        accommodations_option = input("Would you like to find accommodation in " + dest_loc + "? (y/n): ").lower()
        if check_quit(accommodations_option):
            break
        if accommodations_option.startswith('y'):
            accommodations = gpt.find_accommodations(dest_loc)
            print("Here are accommodations in " + dest_loc + ".")
            print(accommodations)
        print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
    else:
        print("❌ Error message: " + paths_data.get("message", "Unknown error"))
