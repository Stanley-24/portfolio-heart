import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SERVICE_ACCOUNT_FILE = os.getenv("../credentials/google_service_account.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")  # Set this to your calendar's ID (usually your email)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Returns the event and the Google Meet link
def create_google_meet_event(summary, description, start_time, end_time, attendee_email=None):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)

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