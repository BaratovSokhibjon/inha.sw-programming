from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import datetime
import pickle
import logging
from rich.console import Console
from rich.panel import Panel
from rich import box

# Suppress OAuth2 verification logs
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
logging.getLogger('google_auth_oauthlib.flow').setLevel(logging.ERROR)

console = Console()
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_PATH = 'credentials/token.pickle'
CREDENTIALS_PATH = 'credentials/credentials.json'

def get_calendar_service():
    """Get or create Google Calendar API service"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                console.print(Panel(
                    "🔐 Opening browser for Google Calendar authentication...",
                    border_style="info",
                    box=box.ROUNDED
                ))
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH,
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Use manual auth flow
                )
                auth_url, _ = flow.authorization_url(prompt='consent')
                console.print(Panel(
                    f"Please visit this URL to authorize the application:\n[link]{auth_url}[/link]",
                    border_style="info",
                    box=box.ROUNDED
                ))
                code = console.input("[bold cyan]Enter the authorization code: [/bold cyan]")
                flow.fetch_token(code=code)
                creds = flow.credentials

                # Save credentials
                os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
                with open(TOKEN_PATH, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                console.print(Panel(
                    f"❌ Authentication failed: {str(e)}",
                    border_style="error",
                    box=box.ROUNDED
                ))
                return None

    return build('calendar', 'v3', credentials=creds, cache_discovery=False)

def create_calendar_event(origin, destination, start_time, duration_seconds, mode):
    """Create a calendar event for the trip"""
    try:
        service = get_calendar_service()

        # Parse ISO format datetime string
        start_datetime = datetime.datetime.fromisoformat(start_time)
        end_datetime = start_datetime + datetime.timedelta(seconds=duration_seconds)

        event = {
            'summary': f'Trip: {origin} to {destination}',
            'location': destination,
            'description': f'Travel from {origin} to {destination} via {mode}',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return True, f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return False, f"Failed to create calendar event: {str(e)}"
