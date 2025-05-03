import requests
import urllib
import os
import dotenv
import math
from utils import *
from rich.table import Table
import datetime
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.console import Console
from rich.columns import Columns
from rich.text import Text
import signal
import sys
import questionary

from utils.gmaps import create_google_maps_link
from utils.common import safe_confirm, safe_input, signal_handler, check_quit, open_url_in_browser, custom_style, suggest_transport
from utils.hotel import find_real_accommodations
from utils import create_calendar_event
from utils.common import exit_event, check_exit, reset_exit

# Theme setup
from utils.interface import dark
console = Console(theme=dark)

# API setup
route_url = "https://graphhopper.com/api/1/route?"

dotenv.load_dotenv()
graphhopper_api_key = os.getenv("GH_API_KEY")
genai_api_key = os.getenv("GEMINI_API_KEY")

# Keyboard interrupt flag
exit_requested = False



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

def select_vehicle_profile():
    """Interactive menu to select vehicle profile with horizontal arrow keys"""
    profiles = {
        "car": "🚗 Car - Standard road vehicle navigation",
        "bike": "🚲 Bike - Bicycle-friendly routes",
        "foot": "🚶 Foot - Walking routes and pedestrian paths",
        "flight": "✈️ flight - Flying transportation options"
    }

    # Use questionary for horizontal selection
    selection = questionary.select(
        "Select transportation mode:",
        choices=list(profiles),
        style=custom_style,
        qmark="",
        use_arrow_keys=True
    ).ask()

    # Handle None result
    if selection is None:
        return "car"  # Default to car if selection is cancelled
    return selection

def print_steps(data, orig, dest, vehicle, orig_lat, orig_lng, dest_lat, dest_lng):
    """
    Prints the route steps with improved formatting using panels and tables.
    Also creates and displays a Google Maps link.
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

    # Create Google Maps link
    maps_url = create_google_maps_link(orig_lat, orig_lng, dest_lat, dest_lng, vehicle)
    console.print(Panel(f"🔗 View in Google Maps: [link={maps_url}]{maps_url}[/link]",
                       title="📍 External Map",
                       border_style="deco",
                       box=box.ROUNDED))

    # Ask if user wants to open the map
    if safe_confirm("Would you like to open this route in Google Maps?"):
        open_url_in_browser(maps_url)

    # Show directions with step panels
    console.print(Panel(f"🧭 Directions from [highlight]{orig}[/highlight] to [highlight]{dest}[/highlight] ({vehicle})",
                       border_style="title",
                       box=box.ROUNDED))

    steps_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    steps_table.add_column("Icon", justify="center", style="highlight")
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

def display_header():
    """Display app header with styled title"""
    header_text = Text("🛣️  TravelGuide - Your Smart Journey Planner", justify="center")
    header_text.stylize("title")
    console.print(Panel(header_text, box=box.DOUBLE))

def should_offer_accommodation(distance_km):
    """Determine if accommodation should be offered based on distance"""
    return distance_km > 100  # Offer accommodation for trips over 100km

def main():
    """Main application flow with improved UI and exit handling"""
    try:
        display_header()

        while not check_exit():
            reset_exit()  # Reset exit flag for new route

            # All checks for exit_requested should now use check_exit()
            vehicle = select_vehicle_profile()
            if check_quit(vehicle) or check_exit():
                break

            loc1 = safe_input("\n🚩 Type in starting location:")
            if loc1 is None or check_quit(loc1) or check_exit():
                break

            # Add exit checks after each operation
            with console.status("Finding location... \n", spinner="dots"):
                orig_status, orig_lat, orig_lng, orig_loc = geo.geocoding(loc1)
                if check_exit():
                    break

            if orig_status != 200:
                console.print(Panel("❌ Could not find starting location",
                                   border_style="error",
                                   box=box.ROUNDED))
                continue

            # Get destination
            loc2 = safe_input("\n🏁 Type in starting location:")
            if loc2 is None or check_quit(loc2) or check_exit():
                break

            # Show loading animation during geocoding
            with console.status("Finding location... \n", spinner="dots"):
                dest_status, dest_lat, dest_lng, dest_loc = geo.geocoding(loc2)
                if check_exit():
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

            if vehicle == "flight":
                try:
                    # Provide a list of common start times for selection
                    start_time_options = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]
                    start_time = questionary.select(
                        "🕒 Please select a start time:",
                        choices=start_time_options,
                        style=custom_style,
                        qmark="",
                        use_arrow_keys=True
                    ).ask()

                    if start_time is None or check_quit(start_time) or check_exit():
                        break

                    with console.status("[deco]Planning your public transit route...[/deco]", spinner="dots"):
                        paths_data, paths_status = gpt.route_public_transportation(orig_loc, dest_loc, start_time)
                        if check_exit():
                            break

                    # Create Google Maps link for public transit
                    maps_url = create_google_maps_link(orig_lat, orig_lng, dest_lat, dest_lng, "flight")
                    console.print(Panel(f"🔗 View in Google Maps: [link={maps_url}]{maps_url}[/link]",
                                       title="📍 Public Transit Route",
                                       border_style="deco",
                                       box=box.ROUNDED))

                    # Ask if user wants to open the map
                    if safe_confirm("Would you like to open this route in Google Maps?"):
                        open_url_in_browser(maps_url)

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
                    if check_exit():
                        break

                # api_info = f"🛣️ Routing API Status: {paths_status}\n🔗 API URL: {paths_url}"
                # console.print(Panel(api_info,
                #                    title="API Details",
                #                    border_style="panel.border",
                #                    box=box.ROUNDED))

            # Process and display route if data is available
            if paths_status == 200 and paths_data is not None and not check_exit():
                travel_time = paths_data["paths"][0]["time"]
                travel_time_in_hour = float(travel_time) / 1000 / 60 / 60
                distance_km = paths_data["paths"][0]["distance"] / 1000

                suggestion = suggest_transport(vehicle, distance_km)
                if suggestion:
                    console.print(Panel(suggestion,
                                    title="🚦 Transport Suggestion",
                                    border_style="highlight",
                                    box=box.ROUNDED))

                    # Ask if user wants to change transport mode
                    if safe_confirm("Would you like to change your transport mode?"):
                        vehicle = select_vehicle_profile()
                        if check_quit(vehicle) or check_exit():
                            break

                # Ask about calendar integration before showing route details
                if safe_confirm("Would you like to add this trip to your Google Calendar?"):
                    # Split days into two weeks and format them for display
                    week1 = [
                        f"Week 1: {(datetime.date.today() + datetime.timedelta(days=i)).strftime('%A, %Y-%m-%d')}"
                        for i in range(7)
                    ]
                    week2 = [
                        f"Week 2: {(datetime.date.today() + datetime.timedelta(days=i)).strftime('%A, %Y-%m-%d')}"
                        for i in range(7, 14)
                    ]

                    # Combine weeks with a separator
                    days_options = week1 + ["------------------"] + week2

                    selected_day = questionary.select(
                        "Select the day for the trip:",
                        choices=days_options,
                        style=custom_style,
                        qmark=""
                    ).ask()

                    if selected_day and selected_day != "------------------":
                        # Split time options into AM/PM groups
                        time_options = [
                            "Morning (5AM-11AM)",
                            "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                            "Afternoon (12PM-5PM)",
                            "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                            "Evening (6PM-10PM)",
                            "18:00", "19:00", "20:00", "21:00", "22:00"
                        ]

                        start_time = questionary.select(
                            "Select start time for the trip:",
                            choices=time_options,
                            style=custom_style,
                            qmark=""
                        ).ask()

                        if start_time and not start_time.startswith(("Morning", "Afternoon", "Evening")):
                            # Remove the "Week X: " prefix from selected_day
                            selected_date = selected_day.split(": ")[1].split(", ")[1]
                            event_datetime = f"{selected_date}T{start_time}:00"

                            success, message = create_calendar_event(
                                orig_loc, dest_loc, event_datetime,
                                int(travel_time / 1000), vehicle
                            )
                            console.print(Panel(message,
                                              title="📅 Calendar Integration",
                                              border_style="panel.border" if success else "error",
                                              box=box.ROUNDED))

                # Display weather information
                weather = OpenMeteo()
                with console.status("[deco]Checking weather conditions...[/deco]", spinner="dots"):
                    curr_weather = weather.get_weather(orig_lat, orig_lng, hours=1)
                    forecast = weather.get_weather(dest_lat, dest_lng, hours=math.ceil(travel_time_in_hour))
                    if check_exit():
                        break
                    weather_advisory = gpt.check_weather_conditions(orig_loc, dest_loc, str(travel_time_in_hour), curr_weather, forecast)

                console.print(Panel(weather_advisory,
                                   title="🌦️ Weather Advisory",
                                   border_style="panel.border",
                                   box=box.ROUNDED))

                # Print route steps with Google Maps link
                print_steps(paths_data, orig_loc, dest_loc, vehicle, orig_lat, orig_lng, dest_lat, dest_lng)
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

                # Only offer accommodation for longer trips
                if should_offer_accommodation(distance_km) and safe_confirm(
                    f"\nThis is a long trip ({distance_km:.1f} km). Would you like to find accommodation in {dest_loc}?"
                ):
                    # Get price range preference
                    price_options = {"low": "Budget", "medium": "Moderate", "high": "Luxury"}
                    # price_panels = []

                    # for key, desc in price_options.items():
                    #     panel = Panel(desc, title=f"[{key}]", border_style="menu.border", box=box.ROUNDED)
                    #     price_panels.append(panel)

                    # console.print(Columns(price_panels, equal=True, expand=True))
                    price_range = questionary.select(
                        "\n💲 Price Range Preference",
                        choices=list(price_options.keys()),
                        style=custom_style,
                        qmark="",
                        use_arrow_keys=True,
                        default="medium"
                    ).ask()

                    if price_range is None:
                        price_range = "medium"  # Default value if None

                    if check_quit(price_range) or check_exit():
                        break

                    # Get AI suggestions using existing method
                    with console.status(f"[deco]Finding places to stay in {dest_loc}...[/deco]", spinner="dots"):
                        ai_accommodations = gpt.find_accommodations(dest_loc)
                        if check_exit():
                            break

                    console.print(Panel(ai_accommodations,
                                       title=f"🤖 AI Accommodation Suggestions for {dest_loc}",
                                       border_style="panel.border",
                                       box=box.ROUNDED))

                    # Add real accommodation links
                    real_accommodations = find_real_accommodations(dest_loc, price_range)

                    console.print(Panel(real_accommodations,
                                       title=f"🏨 Real Accommodation Options in {dest_loc}",
                                       border_style="panel.border",
                                       box=box.ROUNDED))

                    # Ask if user wants to open any accommodation site
                    sites = {
                        "booking": f"https://www.booking.com/searchresults.html?ss={urllib.parse.quote(dest_loc)}",
                        "airbnb": f"https://www.airbnb.com/s/{urllib.parse.quote(dest_loc)}/homes",
                        "hotels": f"https://www.hotels.com/search.do?destination-id={urllib.parse.quote(dest_loc)}",
                        "expedia": f"https://www.expedia.com/Hotel-Search?destination={urllib.parse.quote(dest_loc)}"
                    }

                    open_site = questionary.select(
                        "\n🔗 Open accommodation sites",
                        choices=list(sites.keys()) + ["skip"],
                        style=custom_style,
                        qmark="",
                        use_arrow_keys=True
                    ).ask()

                    if open_site != "skip" and open_site in sites:
                        open_url_in_browser(sites[open_site])

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

            elif not check_exit():
                console.print(Panel(f'❌ Error: {paths_data.get("message", "Unknown error")}',
                                   border_style="error",
                                   box=box.ROUNDED))

            # Ask to plan another route
            if check_exit():
                break

            if not safe_confirm("\nPlan another route?"):
                break

        # Goodbye message
        console.print(Panel("👋 Thank you for using TravelGuide!",
                           border_style="title",
                           box=box.DOUBLE))

    except KeyboardInterrupt:
        os._exit(0)  # Force immediate exit
    except Exception as e:
        console.print(Panel(f"❌ An unexpected error occurred: {str(e)}",
                           border_style="error",
                           box=box.ROUNDED))
        os._exit(1)  # Force immediate exit with error code

if __name__ == "__main__":
    main()
