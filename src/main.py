import requests
import urllib
import os
import dotenv

from utils import *

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

def check_quit(user_input):
    if user_input == "quit" or user_input == "q":
        return True
    else:
        return False

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

    if vehicle == "public":
        start_time = input("🏁 Please provide a start time (e.g. 1pm): ")
        if check_quit(start_time):
            break
        gpt.route_public_transportation(loc1, loc2, start_time)
        accommodations_option = input("Would you like to find accommodation in " + loc2 + "? (y/n): ").lower()
        if check_quit(accommodations_option):
            break
        if accommodations_option.startswith('y'):
            accommodations = gpt.find_accommodations(loc2)
            print("Here are accommodations in " + loc2 + ".")
            print(accommodations)
            print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

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

        if paths_status == 200:
            distance_m = paths_data["paths"][0]["distance"]
            duration_ms = paths_data["paths"][0]["time"]

            miles = distance_m / 1000 / 1.61
            km = distance_m / 1000

            sec = int(duration_ms / 1000 % 60)
            minutes = int(duration_ms / 1000 / 60 % 60)
            hours = int(duration_ms / 1000 / 60 / 60)

            print("📏 Distance Traveled: {:.1f} miles / {:.1f} km".format(miles, km))
            print("⏱️ Trip Duration: {:02d}:{:02d}:{:02d}".format(hours, minutes, sec))
            print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

            # Generate and display AI route summary
            try:
                summary = gpt.generate_route_summary(paths_data, orig_loc[3], dest_loc[3], vehicle)
                print("🤖 AI Route Summary:")
                print(f"💬 {summary}")
                print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
            except Exception as e:
                print(f"⚠️ Couldn't generate route summary: {str(e)}")

            for step in paths_data["paths"][0]["instructions"]:
                path_text = step["text"]
                step_distance = step["distance"]
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

                # Format distance in a more readable way
                if step_distance < 100:
                    distance_str = f"{step_distance:.0f} m"
                else:
                    distance_str = f"{step_distance/1000:.1f} km / {step_distance/1000/1.61:.1f} miles"

                print(f"{direction_arrow}     {path_text} ({distance_str})")
            print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

            voice_option = input("Would you like voice-like instructions? (y/n): ").lower()
            if check_quit(voice_option):
                break
            if voice_option.startswith('y'):
                natural_instructions = gpt.convert_to_natural_instructions(paths_data["paths"][0]["instructions"])
                voice_navigation(natural_instructions)
                print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

            accommodations_option = input("Would you like to find accommodation in " + loc2 + "? (y/n): ").lower()
            if check_quit(accommodations_option):
                break
            if accommodations_option.startswith('y'):
                accommodations = gpt.find_accommodations(loc2)
                print("Here are accommodations in " + loc2 + ".")
                print(accommodations)
                print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
        else:
            print("❌ Error message: " + paths_data.get("message", "Unknown error"))
