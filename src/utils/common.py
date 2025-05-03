from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
import webbrowser
import signal
import questionary
from questionary import Style as QuestionaryStyle
import sys

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
    global exit_requested
    exit_requested = True
    console.print("\n")
    console.print(Panel("⚠️ Program stop requested. Exiting gracefully...",
                        border_style="error",
                        box=box.ROUNDED))
    sys.exit(0)

def safe_input(prompt, choices=None, default=None):
    """
    Enhanced input function with arrow key support for choices
    """
    try:
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
    Enhanced confirm dialog with arrow key support
    """
    try:
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
