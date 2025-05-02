from rich.console import Console
from rich.style import Style

import pathlib
from rich_theme_manager import Theme, ThemeManager


THEMES = [
    Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            
            "question": Style(color="#53599A"),
            "answer" :Style(color= "#def6ca", dim = True ),
            "error": Style(color= "#ce2d4f"),
            "deco": Style(color= "#568259", blink = True),
            "other": Style(color= "#f8bdc4"),
            
            

        },
    ),
   
]

# ............................................................................................................................................................................
theme_dir = pathlib.Path("~/.rich_theme_manager/themes").expanduser()
theme_dir.expanduser().mkdir(parents=True, exist_ok=True)

theme_manager = ThemeManager(theme_dir=theme_dir, themes=THEMES)
theme_manager.list_themes()
print("\n")
