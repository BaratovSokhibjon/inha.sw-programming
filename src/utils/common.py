from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
import webbrowser
import signal
import questionary
from questionary import Style as QuestionaryStyle
import sys
import threading
import os

from .interface import dark
console = Console(theme=dark)

# Custom style for questionary
custom_style = QuestionaryStyle([
    ('question', 'fg:#53599A bold'),
    ('answer', 'fg:#def6ca'),
    ('pointer', 'fg:#568259 bold'),
    ('highlighted', 'fg:#f8bdc4 bold'),
    ('selected', 'fg:#568259'),
])

# Global exit event
exit_event = threading.Event()

def open_url_in_browser(url):
    """Open a URL in the default web browser"""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        console.print(Panel(f"❌ Error opening link: {str(e)}",
                           border_style="error",
                           box=box.ROUNDED))
        return False

def check_quit(user_input):
    """
    Determines if the user input indicates a quit command.
    """
    if user_input.lower() in ["quit", "q", "exit"]:
        return True
    return False

def signal_handler(sig, frame):
    """Handle keyboard interrupts (Ctrl+C)"""
    console.print("\n")
    console.print(Panel("⚠️ Program stop requested. Exiting...",
                        border_style="error",
                        box=box.ROUNDED))
    os._exit(0)  # Force immediate exit

def check_exit():
    """Check if exit has been requested"""
    return exit_event.is_set()

def reset_exit():
    """Reset exit event - useful for new route planning"""
    exit_event.clear()

def safe_input(prompt, choices=None, default=None):
    """
    Enhanced input function with arrow key support for choices and exit checking
    """
    try:
        if exit_event.is_set():
            return None
        if choices:
            result = questionary.select(
                prompt,
                choices=choices,
                default=default,
                style=custom_style,
                qmark=""
            ).ask()
            # Handle None result
            if result is None:
                return ""
        else:
            # Use questionary's text input for free text
            result = questionary.text(
                prompt,
                default=default or "",
                style=custom_style,
                qmark=""
            ).ask()
            # Handle None result
            if result is None:
                return ""
        return result
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
        return ""

def safe_confirm(prompt):
    """
    Enhanced confirm dialog with arrow key support and exit checking
    """
    try:
        if exit_event.is_set():
            return False
        result = questionary.select(
            prompt,
            choices=["Yes", "No"],
            style=custom_style,
            qmark=""
        ).ask()
        # Handle None result
        if result is None:
            return False
        return result == "Yes"
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
        return False

def suggest_transport(mode: str, distance_km: float) -> str:
    """
    Return a warning string if the distance is too long for walking or biking,
    or suggest alternatives based on the distance range.
    mode: one of "car", "bike", "foot"/"walk", "public", or "flight"
    distance_km: the total trip distance in kilometers
    """
    # Normalize GraphHopper's "foot" to our "walk"
    if mode == "foot":
        key = "walk"
    else:
        key = mode

    if key == "walk":
        if distance_km > 10:
            return f"⚠️ {distance_km:.1f} km is a long walk! Maybe try a bike 🚲 or car 🚗 instead?"
        elif distance_km > 5:
            return f"ℹ️ {distance_km:.1f} km is a moderate walk. Ensure you're prepared!"
    elif key == "bike":
        if distance_km > 30:
            return f"⚠️ {distance_km:.1f} km is a long trip for a bike! Maybe use a car 🚗 or train 🚆 instead?"
        elif distance_km > 15:
            return f"ℹ️ {distance_km:.1f} km is a moderate bike ride. Stay hydrated!"
    elif key == "car":
        if distance_km < 2:
            return f"ℹ️ {distance_km:.1f} km is a short trip. Consider walking 🚶 or biking 🚲 instead!"
        elif distance_km > 1000:
            return f"⚠️ {distance_km:.1f} km is a very long trip for a car. Consider taking a flight ✈️ instead!"
    elif key == "public":
        if distance_km < 1:
            return f"ℹ️ {distance_km:.1f} km is very short. Walking 🚶 might be a better option!"
        elif distance_km > 500:
            return f"⚠️ {distance_km:.1f} km is a long trip. Consider taking a flight ✈️ for faster travel!"
    elif key == "flight":
        if distance_km < 200:
            return f"ℹ️ {distance_km:.1f} km is a short distance for a flight. Consider a car 🚗 or train 🚆 instead!"
        elif distance_km > 15000:
            return f"⚠️ {distance_km:.1f} km is an extremely long trip. Ensure you plan for layovers and rest!"

    return ""
