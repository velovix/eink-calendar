import datetime
import logging
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from xdg import BaseDirectory

from .event import Event

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class Client:
    def __init__(self) -> None:
        self._creds = self._get_credentials()
        self._service = build("calendar", "v3", credentials=self._creds)

    def get_events(self) -> list[Event]:
        calendars = self._service.calendarList().list().execute()

        now = datetime.datetime.utcnow()
        time_min = now - datetime.timedelta(hours=20)

        # Only look at calendars the user selects on their Google Calendar view
        selected_calendars = [c for c in calendars["items"] if c.get("selected", False)]

        events = []
        for calendar in selected_calendars:
            result = (
                self._service.events()
                .list(
                    calendarId=calendar["id"],
                    timeMin=time_min.isoformat() + "Z",
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events += [Event(calendar, e) for e in result.get("items", [])]

        # Filter for today's events
        events = [e for e in events if e.start_time.date() == datetime.date.today()]

        return self._sort_events(events)

    def _get_credentials(self) -> Credentials:
        creds = None
        data_path = Path(BaseDirectory.save_data_path("eink_calendar"))

        credentials_file = data_path / "credentials.json"
        if not credentials_file.is_file():
            logging.error(f"Missing credentials file at: {credentials_file}")
            sys.exit(1)

        token = data_path / "token.json"
        if token.is_file():
            creds = Credentials.from_authorized_user_file(str(token), SCOPES)
        if creds is None or not creds.valid:
            if creds is not None and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), SCOPES,
                )
                creds = flow.run_local_server(port=0)
            token.write_text(creds.to_json())

        return creds

    def _sort_events(self, events: list[Event]) -> list[Event]:
        """Sorts events by their start time, with all-day events always at the start."""
        all_days = [e for e in events if e.all_day]
        all_days = sorted(all_days, key=lambda e: e.start_time)
        non_all_days = [e for e in events if not e.all_day]
        non_all_days = sorted(non_all_days, key=lambda e: e.start_time)

        return all_days + non_all_days
