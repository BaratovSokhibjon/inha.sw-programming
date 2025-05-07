import requests
from rich.panel import Panel
from rich import box
from rich.console import Console
from utils.interface import dark

console = Console(theme=dark)

class OpenMeteo:
    """
    Provides functionality to interact with the Open-Meteo weather API.
    """

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
