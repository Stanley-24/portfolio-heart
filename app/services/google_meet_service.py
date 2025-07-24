import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

TOKEN_PATH = "app/credentials/token.json"
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")  # Set this to your calendar's ID (usually your email)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service

# Returns the event and the Google Meet link
def create_google_meet_event(summary, description, start_time, end_time, attendee_email=None):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(datetime.utcnow().timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "attendees": [{"email": attendee_email}] if attendee_email else [],
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=1
    ).execute()

    meet_link = created_event.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
    return created_event, meet_link 