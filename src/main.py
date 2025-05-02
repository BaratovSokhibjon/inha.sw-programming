import requests
import urllib
import os
import dotenv
import math
from utils import *
from rich.console import Console
from rich.progress import track
from utils import interface
import time
from rich.table import Table
import datetime
#............................................................................................................................ INTERFACE ...............................

dark = interface.theme_manager.get("dark")
interface.theme_manager.preview_theme(dark)
console = Console(theme=dark)


# ...............................................................................................................................................................................
route_url = "https://graphhopper.com/api/1/route?"

dotenv.load_dotenv()
graphhopper_api_key = os.getenv("GH_API_KEY")
genai_api_key = os.getenv("GEMINI_API_KEY")

# Validate API keys
if not graphhopper_api_key:
    console.print("❌ Error: Graphhopper API key (GH_API_KEY) is not set.", style="error")
    exit(1)
if not genai_api_key:
    console.print("❌ Error: Gemini API key (GEMINI_API_KEY) is not set.", style = "error")
    exit(1)

genai_model = "gemini-2.0-flash"

geo = Geocoding(graphhopper_api_key)
gpt = Genai(genai_api_key, genai_model)


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
            console.print("The travel duration exceeds the available forecast range.\n Weather conditions will be shown for up to the next 168 hours only.", style ="error")

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
            console.print(f"❌ Error parsing weather data: {str(e)}",style = "error") 



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
    """
    Determines if the user input indicates a quit command.

    This function evaluates whether the provided input matches either of the
    designated commands for quitting: "quit" or "q". It is case-sensitive and
    intends to provide a simple mechanism to check for termination instructions.

    Parameters:
    user_input: str
        The input string provided by the user to be evaluated.

    Returns:
    bool
        True if the input matches "quit" or "q", otherwise False.
    """
    if user_input == "quit" or user_input == "q":
        return True
    else:
        return False

def print_steps(data, orig, dest):
    """
    Prints the route steps, including distance, duration, and individual step instructions with corresponding symbols.

    This function processes the given route data and computes both the overall trip summary
    and detailed step-by-step instructions. The overall summary includes the trip distance in
    miles and kilometers and the duration in hours, minutes, and seconds. For each step in
    the instruction set, the function determines the corresponding direction symbol and prints
    the instruction along with the step distance in a readable format. Additionally, attempts
    are made to generate an AI-generated summary of the route using a separate function.

    Parameters:
        data (dict): The route data containing paths and instructions. It includes information
            about the overall trip such as distance and duration, as well as detailed step
            instructions.
        orig (str): The original starting location of the trip.
        dest (str): The destination for the trip.

    Raises:
        Exception: If an error occurs while generating the AI-driven route summary.
    """
    distance_m = data["paths"][0]["distance"]
    duration_ms = data["paths"][0]["time"]

    miles = distance_m / 1000 / 1.61
    km = distance_m / 1000

    sec = int(duration_ms / 1000 % 60)
    minutes = int(duration_ms / 1000 / 60 % 60)
    hours = int(duration_ms / 1000 / 60 / 60)

    console.print("📏 Distance Traveled: {:.1f} miles / {:.1f} km".format(miles, km), style="answer")
    console.print("⏱️ Trip Duration: {:02d}:{:02d}:{:02d}".format(hours, minutes, sec),style="answer")
    console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")

    try:
        summary = gpt.generate_route_summary(paths_data, orig, dest, vehicle)
        console.print("🤖 AI Route Summary:", style ="deco")
        for i in track(range(5), description="Calculating your route..."):
            time.sleep(0.1)  # Simulate work being done
        console.print(f"💬 {summary}", style="answer")
        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")
    except Exception as e:
        console.print(f"⚠️ Couldn't generate route summary: {str(e)}",style="error")

    for step in data["paths"][0]["instructions"]:
        path_text = step["text"]
        time.sleep(0.1)
        # Choose the appropriate direction arrow based on the text
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
            console.print(f"{direction_arrow}     {path_text} ({distance_str})",style = "answer")
        else:
            console.print(f"{direction_arrow}     {path_text}",style="answer")



while True:
    
    console.print("🚗 Vehicle profiles available on Graphhopper: 🚗", style = "question")
    console.print("🚗 car, 🚲 bike, 🚶 foot, 🚌 public",style = "question")
    profile = ["car", "bike", "foot", "public"]
    console.print("🔍 Enter a vehicle profile from the list above: ", style="question")
    vehicle = input().strip().lower()

    if check_quit(vehicle):
        break
    elif vehicle not in profile:
        vehicle = "car"
        console.print("⚠️ No valid vehicle profile was entered. Using the car profile.", style="other")

    loc1 = console.input("[question]🏁 Starting Location: [/question] ")
    if check_quit(loc1):
        break
    orig_status, orig_lat, orig_lng, orig_loc = geo.geocoding(loc1)

    loc2 = console.input("[question]🏁 Destination: [/question]")
    if check_quit(loc2):
        break
    dest_status, dest_lat, dest_lng, dest_loc = geo.geocoding(loc2)

    console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")

    paths_status = 404
    paths_data = None
    if vehicle == "public":
        try:
            start_time = console.input("🏁 [question]Please provide a start time (e.g. 1pm):[/question] ")
            if check_quit(start_time):
                break
            paths_data, paths_status = gpt.route_public_transportation(orig_loc, dest_loc, start_time)
        except Exception as e:
            console.print(f"⚠️ Couldn't generate route summary: {str(e)}", style="error")

    elif orig_status == 200 and dest_status == 200:
        op = "&point=" + str(orig_lat) + "%2C" + str(orig_lng)
        dp = "&point=" + str(dest_lat) + "%2C" + str(dest_lng)
        paths_url = route_url + urllib.parse.urlencode(
            {"key": graphhopper_api_key, "vehicle": vehicle}
        ) + op + dp

        response = requests.get(paths_url)
        paths_status = response.status_code
        paths_data = response.json()

        console.print(f"🛣️ Routing API Status: {paths_status}", style="answer")
        console.print(f"🔗 Routing API URL:\n{paths_url}",style="answer")
        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")

        icon = "🚗" if vehicle == "car" else "🚲" if vehicle == "bike" else "🚶"
        
        

    if paths_status == 200 and paths_data is not None:
        travel_time = paths_data["paths"][0]["time"]
        travel_time_in_hour = float(travel_time) /1000/ 60/ 60
        weather = OpenMeteo()
        curr_weather = weather.get_weather(orig_lat, orig_lng, hours= 1)
        forecast = weather.get_weather(dest_lat, dest_lng, hours=math.ceil(travel_time_in_hour))

        weather_advisory = gpt.check_weather_conditions(orig_loc, dest_loc, str(travel_time_in_hour), curr_weather, forecast)
        console.print("🌦️ Weather Advisory:", style = "other")
        
        for i in track(range(10), description=f"[deco]Chasing Clouds...[/deco]"):
            time.sleep(0.1)  # Simulate work being done

        console.print(weather_advisory, style="answer")
        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")
        console.print(
            f"🧭 Directions from {orig_loc} to {dest_loc} by {icon} {vehicle}", style="answer"
        )

        print_steps(paths_data, orig_loc, dest_loc)
        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")

        voice_option = console.input("[question]Would you like voice-like instructions? (y/n): [/question]").lower()
        if check_quit(voice_option):
            break
        if voice_option.startswith('y'):
            natural_instructions = gpt.convert_to_natural_instructions(paths_data["paths"][0]["instructions"])
            voice_navigation(natural_instructions)

        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")
        accommodations_option = console.input(f"[question]Would you like to find accommodation in {dest_loc}? (y/n): [/question]").lower()
        if check_quit(accommodations_option):
            break
        if accommodations_option.startswith('y'):
            accommodations = gpt.find_accommodations(dest_loc)
            for i in track(range(10), description=f"[deco]Exploring hidden gems...[/deco]"):
                time.sleep(0.1)  
            console.print(f"Here are accommodations in {dest_loc}.",style= "answer")
            console.print(accommodations,style = "answer")
        console.print("------------------------------------------------------------------------------------------------------------------------------------",style="deco")
    else:
        console.print(f'❌ Error message: {paths_data.get("message", "Unknown error")}',style="error")


    table = Table(title="Trip Summary")
    seconds = float(travel_time) // 1000
    formatted_time = str(datetime.timedelta(seconds = seconds))

    table.add_column("Departure", justify="right", style="deco", no_wrap=True)
    table.add_column("Arrival", style="deco")
    table.add_column("Duration", style = "deco")
    table.add_column("Transportation", justify="right", style="deco")

    table.add_row(f"{loc1.title()}", f"{loc2.title()}", f"{formatted_time}", f"{vehicle.title()}")
    

    
    console.print(table)
