from rich.style import Style
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
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.columns import Columns
from rich_theme_manager import Theme, ThemeManager
from rich_menu import Menu
from rich.align import Align
from rich.text import Text
import pathlib
import signal
import sys

# Theme setup
THEMES = [
    Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "question": Style(color="#53599A", bold=True),
            "answer": Style(color="#def6ca"),
            "error": Style(color="#ce2d4f"),
            "deco": Style(color="#568259"),
            "highlight": Style(color="#f8bdc4", bold=True),
            "title": Style(color="#FF875F", bold=True),  # Ensure this style is defined
            "panel.border": Style(color="#568259"),
            "menu.border": Style(color="#53599A"),
        },
    ),
    Theme(
        name="light",
        description="Light mode theme",
        tags=["light"],
        styles={
            "question": Style(color="#3a539b", bold=True),
            "answer": Style(color="#006400"),
            "error": Style(color="#B22222"),
            "deco": Style(color="#2E8B57"),
            "highlight": Style(color="#9932CC", bold=True),
            "title": Style(color="#CD5C5C", bold=True),
            "panel.border": Style(color="#2E8B57"),
            "menu.border": Style(color="#3a539b"),
        },
    ),
]

# Initialize theme manager
theme_dir = pathlib.Path("~/.rich_theme_manager/themes").expanduser()
theme_manager = ThemeManager(theme_dir=theme_dir, themes=THEMES)
dark = theme_manager.get("dark")

# Ensure 'menu.border' and 'panel.border' styles are defined
if "menu.border" not in dark.styles:
    dark.styles["menu.border"] = Style(color="white")  # Default to white if not defined
if "highlight" not in dark.styles:
    dark.styles["highlight"] = Style(color="yellow", bold=True)  # Default to yellow if not defined
if "panel.border" not in dark.styles:
    dark.styles["panel.border"] = Style(color="white")  # Default to white if not defined
if "title" not in dark.styles:
    dark.styles["title"] = Style(color="#FF875F", bold=True)  # Ensure 'title' style is defined

console = Console(theme=dark)

# API setup
route_url = "https://graphhopper.com/api/1/route?"

dotenv.load_dotenv()
graphhopper_api_key = os.getenv("GH_API_KEY")
genai_api_key = os.getenv("GEMINI_API_KEY")

# Keyboard interrupt flag
exit_requested = False

def signal_handler(sig, frame):
    """Handle keyboard interrupts (Ctrl+C)"""
    global exit_requested
    exit_requested = True
    console.print("\n")
    console.print(Panel("⚠️ Program stop requested. Exiting gracefully...",
                        border_style="error",
                        box=box.ROUNDED))
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Validate API keys
if not graphhopper_api_key:
    console.print(Panel("❌ Error: Graphhopper API key (GH_API_KEY) is not set.",
                        border_style="error",
                        box=box.ROUNDED))
    exit(1)
if not genai_api_key:
    console.print(Panel("❌ Error: Gemini API key (GEMINI_API_KEY) is not set.",
                        border_style="error",
                        box=box.ROUNDED))
    exit(1)

genai_model = os.getenv("GENAI_MODEL", "gemini-2.0-flash")

geo = Geocoding(graphhopper_api_key)
gpt = Genai(genai_api_key, genai_model)

class OpenMeteo:
    """
    Provides functionality to interact with the Open-Meteo weather API.
    """

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, lat, lng, hours=12):
        global exit_requested
        if exit_requested:
            return None

        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}"
            f"&hourly=temperature_2m,weathercode,wind_speed_10m&timezone=auto"
        )
        response = requests.get(url)
        data = response.json()
        if (hours > 168):
            console.print(Panel("⚠️ The travel duration exceeds the available forecast range.\n Weather conditions will be shown for up to the next 168 hours only.",
                                border_style="error",
                                box=box.ROUNDED))

        hourly = data.get("hourly", {})
        available_hours = len(hourly.get("time", []))

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
            console.print(Panel(f"❌ Error parsing weather data: {str(e)}",
                                border_style="error",
                                box=box.ROUNDED))

    def decode_weather(self, code):
        # Weather code mapping with emojis
        weather_map = {
            0: "☀️ clear sky",
            1: "🌤️ mainly clear",
            2: "⛅ partly cloudy",
            3: "☁️ overcast",
            45: "🌫️ fog",
            48: "❄️ depositing rime fog",
            51: "🌦️ light drizzle",
            61: "🌧️ light rain",
            71: "❄️ light snow",
            95: "⛈️ thunderstorm",
            96: "🌩️ thunderstorm w/ hail"
        }
        return weather_map.get(code, "unknown")

def check_quit(user_input):
    """
    Determines if the user input indicates a quit command.
    """
    if user_input.lower() in ["quit", "q", "exit"]:
        return True
    return False

def display_header():
    """Display app header with styled title"""
    header_text = Text("🛣️  TravelGuide - Your Smart Journey Planner", justify="center")
    header_text.stylize("title")
    console.print(Panel(header_text, box=box.DOUBLE))
    console.print(Panel("Press [bold red]Ctrl+C[/bold red] at any time to exit the program.",
                        border_style="deco",
                        box=box.ROUNDED))

def select_vehicle_profile():
    """Interactive menu to select vehicle profile"""
    profiles = {
        "car": "🚗 Car - Standard road vehicle navigation",
        "bike": "🚲 Bike - Bicycle-friendly routes",
        "foot": "🚶 Foot - Walking routes and pedestrian paths",
        "public": "🚌 Public - Public transportation options"
    }

    profile_panels = []
    for key, desc in profiles.items():
        panel = Panel(desc, title=f"[{key}]", border_style="menu.border", box=box.ROUNDED)
        profile_panels.append(panel)

    columns = Columns(profile_panels, equal=True, expand=True)

    console.print(columns)

    options = list(profiles.keys())
    selection = Prompt.ask("Enter your choice", choices=options, default="car")

    return selection

def print_steps(data, orig, dest, vehicle):
    """
    Prints the route steps with improved formatting using panels and tables.
    """
    global exit_requested
    if exit_requested:
        return

    distance_m = data["paths"][0]["distance"]
    duration_ms = data["paths"][0]["time"]

    miles = distance_m / 1000 / 1.61
    km = distance_m / 1000

    sec = int(duration_ms / 1000 % 60)
    minutes = int(duration_ms / 1000 / 60 % 60)
    hours = int(duration_ms / 1000 / 60 / 60)

    # Create summary table
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Info", style="highlight")
    summary_table.add_column("Value", style="answer")

    summary_table.add_row("📏 Distance", f"{miles:.1f} miles / {km:.1f} km")
    summary_table.add_row("⏱️ Duration", f"{hours:02d}:{minutes:02d}:{sec:02d}")

    console.print(Panel(summary_table,
                        title="📊 Trip Summary",
                        border_style="panel.border",
                        box=box.ROUNDED))

    # Generate AI summary with progress animation
    try:
        with console.status("[deco]AI is analyzing your route...[/deco]", spinner="dots"):
            summary = gpt.generate_route_summary(data, orig, dest, vehicle)
            if exit_requested:
                return

        console.print(Panel(f"{summary}",
                           title="🤖 AI Route Summary",
                           border_style="panel.border",
                           box=box.ROUNDED))
    except Exception as e:
        console.print(Panel(f"⚠️ Couldn't generate route summary: {str(e)}",
                           border_style="error",
                           box=box.ROUNDED))

    # Show directions with step panels
    console.print(Panel(f"🧭 Directions from [highlight]{orig}[/highlight] to [highlight]{dest}[/highlight] ({vehicle})",
                       border_style="title",
                       box=box.ROUNDED))

    steps_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    steps_table.add_column("Icon", justify="center", style="deco")
    steps_table.add_column("Direction", style="answer")

    for step in data["paths"][0]["instructions"]:
        if exit_requested:
            return

        path_text = step["text"]

        # Choose the appropriate direction arrow based on the text
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
        else:
            direction_arrow = "➡️"  # default

        if "distance" in step:
            step_distance = step["distance"]
            # Format distance in a more readable way
            if step_distance < 100:
                distance_str = f"{step_distance:.0f} m"
            else:
                distance_str = f"{step_distance / 1000:.1f} km / {step_distance / 1000 / 1.61:.1f} miles"

            steps_table.add_row(direction_arrow, f"{path_text} ({distance_str})")
        else:
            steps_table.add_row(direction_arrow, path_text)

    console.print(steps_table)

def safe_input(prompt, **kwargs):
    """
    Wrapper for input functions to handle keyboard interrupts
    """
    try:
        return Prompt.ask(prompt, **kwargs)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
        return None  # Will not reach here, but included for completeness

def safe_confirm(prompt):
    """
    Wrapper for confirm to handle keyboard interrupts
    """
    try:
        return Confirm.ask(prompt)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
        return False  # Will not reach here, but included for completeness

def main():
    """Main application flow with improved UI"""
    global exit_requested
    try:
        display_header()

        while not exit_requested:
            # Select vehicle profile with visual menu
            vehicle = select_vehicle_profile()
            if check_quit(vehicle) or exit_requested:
                break

            # Get starting location
            loc1 = safe_input("\n🏁 [question]Starting Location[/question]")
            if loc1 is None or check_quit(loc1) or exit_requested:
                break

            # Show loading animation during geocoding
            with console.status("Finding location...", spinner="dots"):
                orig_status, orig_lat, orig_lng, orig_loc = geo.geocoding(loc1)
                if exit_requested:
                    break

            if orig_status != 200:
                console.print(Panel("❌ Could not find starting location",
                                   border_style="error",
                                   box=box.ROUNDED))
                continue

            # Get destination
            loc2 = safe_input("\n🏁 [question]Destination[/question]")
            if loc2 is None or check_quit(loc2) or exit_requested:
                break

            # Show loading animation during geocoding
            with console.status("Finding location...", spinner="dots"):
                dest_status, dest_lat, dest_lng, dest_loc = geo.geocoding(loc2)
                if exit_requested:
                    break

            if dest_status != 200:
                console.print(Panel("❌ Could not find destination",
                                   border_style="error",
                                   box=box.ROUNDED))
                continue

            console.print(Panel(f"🚩 From: [highlight]{orig_loc}[/highlight]\n🏁 To: [highlight]{dest_loc}[/highlight]",
                               title="Your Route",
                               border_style="panel.border",
                               box=box.ROUNDED))

            paths_status = 404
            paths_data = None

            if vehicle == "public":
                try:
                    start_time = safe_input("🕒 [question]Please provide a start time[/question]", default="1pm")
                    if start_time is None or check_quit(start_time) or exit_requested:
                        break

                    with console.status("[deco]Planning your public transit route...[/deco]", spinner="dots"):
                        paths_data, paths_status = gpt.route_public_transportation(orig_loc, dest_loc, start_time)
                        if exit_requested:
                            break
                except Exception as e:
                    console.print(Panel(f"⚠️ Couldn't generate route: {str(e)}",
                                       border_style="error",
                                       box=box.ROUNDED))

            elif orig_status == 200 and dest_status == 200:
                op = "&point=" + str(orig_lat) + "%2C" + str(orig_lng)
                dp = "&point=" + str(dest_lat) + "%2C" + str(dest_lng)
                paths_url = route_url + urllib.parse.urlencode(
                    {"key": graphhopper_api_key, "vehicle": vehicle}
                ) + op + dp

                with console.status("[deco]Calculating your route...[/deco]", spinner="dots"):
                    response = requests.get(paths_url)
                    paths_status = response.status_code
                    paths_data = response.json()
                    if exit_requested:
                        break

                api_info = f"🛣️ Routing API Status: {paths_status}\n🔗 API URL: {paths_url}"
                console.print(Panel(api_info,
                                   title="API Details",
                                   border_style="panel.border",
                                   box=box.ROUNDED))

            # Process and display route if data is available
            if paths_status == 200 and paths_data is not None and not exit_requested:
                travel_time = paths_data["paths"][0]["time"]
                travel_time_in_hour = float(travel_time) / 1000 / 60 / 60

                # Display weather information
                weather = OpenMeteo()
                with console.status("[deco]Checking weather conditions...[/deco]", spinner="dots"):
                    curr_weather = weather.get_weather(orig_lat, orig_lng, hours=1)
                    forecast = weather.get_weather(dest_lat, dest_lng, hours=math.ceil(travel_time_in_hour))
                    if exit_requested:
                        break
                    weather_advisory = gpt.check_weather_conditions(orig_loc, dest_loc, str(travel_time_in_hour), curr_weather, forecast)

                console.print(Panel(weather_advisory,
                                   title="🌦️ Weather Advisory",
                                   border_style="panel.border",
                                   box=box.ROUNDED))

                # Print route steps
                print_steps(paths_data, orig_loc, dest_loc, vehicle)
                if exit_requested:
                    break

                # Voice navigation option
                voice_option = safe_confirm("Would you like voice-like instructions?")
                if exit_requested or voice_option is None:
                    break

                if voice_option:
                    with console.status("[deco]Preparing voice navigation...[/deco]", spinner="dots"):
                        natural_instructions = gpt.convert_to_natural_instructions(paths_data["paths"][0]["instructions"])
                        if exit_requested:
                            break
                    voice_navigation(natural_instructions)

                # Accommodation option
                accommodations_option = safe_confirm(f"Would you like to find accommodation in {dest_loc}?")
                if exit_requested or accommodations_option is None:
                    break

                if accommodations_option:
                    with console.status(f"[deco]Finding places to stay in {dest_loc}...[/deco]", spinner="dots"):
                        accommodations = gpt.find_accommodations(dest_loc)
                        if exit_requested:
                            break

                    console.print(Panel(accommodations,
                                       title=f"🏨 Accommodations in {dest_loc}",
                                       border_style="panel.border",
                                       box=box.ROUNDED))

                # Create final trip summary
                seconds = float(travel_time) // 1000
                formatted_time = str(datetime.timedelta(seconds=seconds))

                table = Table(title="🚗 Trip Summary", box=box.DOUBLE, title_style="title")
                table.add_column("Departure", justify="right", style="highlight")
                table.add_column("Arrival", style="highlight")
                table.add_column("Duration", style="answer")
                table.add_column("Transportation", style="answer")

                table.add_row(f"{loc1.title()}", f"{loc2.title()}", f"{formatted_time}", f"{vehicle.title()}")
                console.print(table)

            elif not exit_requested:
                console.print(Panel(f'❌ Error: {paths_data.get("message", "Unknown error")}',
                                   border_style="error",
                                   box=box.ROUNDED))

            # Ask to plan another route
            if exit_requested:
                break

            if not safe_confirm("\nPlan another route?"):
                break

        # Goodbye message
        console.print(Panel("👋 Thank you for using TravelGuide!",
                           border_style="title",
                           box=box.DOUBLE))

    except KeyboardInterrupt:
        # This should be caught by the signal handler, but just in case
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        console.print(Panel(f"❌ An unexpected error occurred: {str(e)}",
                           border_style="error",
                           box=box.ROUNDED))
        sys.exit(1)

if __name__ == "__main__":
    main()
