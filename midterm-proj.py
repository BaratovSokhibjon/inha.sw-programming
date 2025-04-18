import requests
import urllib.parse
import dotenv
import os
import google.generativeai as genai
import pyttsx3


dotenv.load_dotenv()
route_url = "https://graphhopper.com/api/1/route?"
key = os.getenv("GH_API_KEY")

genai_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=genai_api_key)
gpt_model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize the TTS engine
engine = pyttsx3.init()

def parse_natural_language_input(input_text):
    """Convert natural language input into structured location data using Gemini"""
    prompt = f"Extract specific location information from: '{input_text}' and return it as a JSON object."
    try:
        response = gpt_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error parsing input: {str(e)}"

def generate_route_summary(paths_data, origin, destination, vehicle):
    """Generate a natural language summary of the route using Gemini"""
    distance = paths_data["paths"][0]["distance"] / 1000
    duration = paths_data["paths"][0]["time"] / (1000 * 60)

    key_points = [step["text"] for step in paths_data["paths"][0]["instructions"][:5]]
    prompt = (
        f"Summarize a {vehicle} route from {origin} to {destination}. "
        f"Distance: {distance:.1f}km, Duration: {duration:.0f} minutes. "
        f"Key instructions: {', '.join(key_points[:3])}."
    )

    try:
        response = gpt_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"

def convert_to_voice_instructions(instructions):
    """Convert technical instructions to natural voice-like navigation"""
    instructions_text = "\n".join([f"{i+1}. {step['text']} ({step['distance']}m)"
                                   for i, step in enumerate(instructions[:10])])

    prompt = (
        f"Convert these technical navigation instructions to natural, voice-like navigation:\n"
        f"{instructions_text}\n\nMake them sound like a friendly GPS voice. Keep each instruction concise."
    )

    try:
        response = gpt_model.generate_content(prompt)
        return response.text.split('\n') # Return as a list of instructions
    except Exception as e:
        return [f"Unable to generate voice instructions: {str(e)}"]

def speak_instruction(text):
    """Speak the given text using the device speaker."""
    engine.say(text)
    engine.runAndWait()

def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode(
        {"q": location, "limit": "1", "key": key}
    )
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif state:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(
            f"🌍 Geocoding API URL for {new_loc} (Location Type: {value})\n{url}"
        )
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print("❌ Error: " + str(json_status))
            print("❌ Geocode API status: " + str(json_status) +
                  "\nError message: " + json_data["message"])
    return json_status, lat, lng, new_loc

while True:
    print("\n✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
    print("🚗 Vehicle profiles available on Graphhopper: 🚗")
    print("✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
    print("🚗 car, 🚲 bike, 🚶 foot")
    print("✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
    print("📢 Options: 'voice' for natural voice instructions")
    print("✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
    profile = ["car", "bike", "foot"]
    vehicle = input("🔍 Enter a vehicle profile from the list above: ").strip().lower()

    if vehicle in ["quit", "q"]:
        break
    elif vehicle not in profile:
        vehicle = "car"
        print("⚠️ No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("🏁 Starting Location: ")
    if loc1 == "quit" or loc1 == "q":
        break
    orig_status, orig_lat, orig_lng, orig_loc = geocoding(loc1, key)

    loc2 = input("🏁 Destination: ")
    if loc2 == "quit" or loc2 == "q":
        break
    dest_status, dest_lat, dest_lng, dest_loc = geocoding(loc2, key)

    print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")

    if orig_status == 200 and dest_status == 200:
        op = "&point=" + str(orig_lat) + "%2C" + str(orig_lng)
        dp = "&point=" + str(dest_lat) + "%2C" + str(dest_lng)
        paths_url = route_url + urllib.parse.urlencode(
            {"key": key, "vehicle": vehicle}
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
                summary = generate_route_summary(paths_data, orig_loc[3], dest_loc[3], vehicle)
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
            if voice_option.startswith('y'):
                print("\n🔊 Voice Navigation:")
                voice_instructions = convert_to_voice_instructions(paths_data["paths"][0]["instructions"])
                engine = pyttsx3.init() # Initialize engine here
                for instruction in voice_instructions:
                    if instruction.strip():
                        print(f"🎙️ Speaking: {instruction.strip()}")
                        engine.say(instruction.strip())
                        engine.runAndWait()
                engine.stop() # Properly stop the engine
                print("🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹🔸🔹")
        else:
            print("❌ Error message: " + paths_data.get("message", "Unknown error"))
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")