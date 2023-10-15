from pathlib import Path
import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .event import Event

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class Client:
    def __init__(self):
        self._creds = self._get_credentials()
        self._service = build("calendar", "v3", credentials=self._creds)

    def get_events(self) -> list[Event]:
        calendars = self._service.calendarList().list().execute()

        now = datetime.datetime.utcnow()
        time_min = now - datetime.timedelta(hours=3)

        events = []
        for calendar in calendars["items"]:
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
        events = [e for e in events if e.start_time.day == datetime.datetime.now().day]

        return events

    def _get_credentials(self) -> Credentials:
        creds = None

        token = Path("token.json")
        if token.is_file():
            creds = Credentials.from_authorized_user_file(str(token), SCOPES)
        if creds is None or not creds.valid:
            if creds is not None and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            token.write_text(creds.to_json())

        return creds

