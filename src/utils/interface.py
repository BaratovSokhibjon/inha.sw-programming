from rich.console import Console
from rich.style import Style

import pathlib
from rich_theme_manager import Theme, ThemeManager

from rich import box
from rich.panel import Panel
from rich.text import Text

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

console = Console(theme=dark, width=100, height=30)

# Ensure 'menu.border' and 'panel.border' styles are defined
if "menu.border" not in dark.styles:
    dark.styles["menu.border"] = Style(color="white")  # Default to white if not defined
if "highlight" not in dark.styles:
    dark.styles["highlight"] = Style(color="yellow", bold=True)  # Default to yellow if not defined
if "panel.border" not in dark.styles:
    dark.styles["panel.border"] = Style(color="white")  # Default to white if not defined
if "title" not in dark.styles:
    dark.styles["title"] = Style(color="#FF875F", bold=True)  # Ensure 'title' style is defined
