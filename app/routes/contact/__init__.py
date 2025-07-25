from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.contact import BookCall, BookCallCreate, Message, MessageCreate
import uuid
from datetime import datetime, timedelta
from app.routes.auth import get_current_admin
from app.services.email_service import send_contact_message_with_zoho, send_booking_confirmation_with_zoho
from app.services.google_meet_service import create_google_meet_event
from app.core.database import get_db
from app.models.contact import Lead
from sqlalchemy.orm import Session

router = APIRouter()

# Fake in-memory DBs
fake_bookcall_db = []
fake_message_db = []

# Helper: validate book call fields
def validate_bookcall(data: BookCallCreate):
    if not data.name or not data.email or not data.preferred_datetime or not data.video_call_provider:
        raise HTTPException(status_code=400, detail="All fields except message and link are required.")

# Helper: validate message fields
def validate_message(data: MessageCreate):
    if not data.name or not data.email or not data.message:
        raise HTTPException(status_code=400, detail="Name, email, and message are required.")

@router.post("/book", summary="Book a Call")
def book_call(data: BookCallCreate, db: Session = Depends(get_db)):
    missing = []
    if not data.name:
        missing.append("name")
    if not data.email:
        missing.append("email")
    if not data.preferred_datetime:
        missing.append("preferred_datetime")
    if not data.video_call_provider:
        missing.append("video_call_provider")
    if missing:
        return {"message": f"Missing required fields: {', '.join(missing)}", "success": False}
    allowed_providers = {"google_meet"}
    if data.video_call_provider not in allowed_providers:
        return {"message": f"Invalid video_call_provider. Allowed: {', '.join(allowed_providers)}", "success": False}
    new_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    # Create Google Meet event
    try:
        start_time = data.preferred_datetime
        end_time = (datetime.fromisoformat(start_time) + timedelta(minutes=30)).isoformat()
        event, meet_link = create_google_meet_event(
            summary=f"Call with {data.name}",
            description=data.message or "",
            start_time=start_time,
            end_time=end_time,
            attendee_email=data.email
        )
    except Exception as e:
        return {"message": f"Failed to create Google Meet event: {str(e)}", "success": False}
    payload = {**data.model_dump(), "video_call_link": meet_link}
    new_call = BookCall(
        id=new_id,
        contacted_at=now,
        calendar_event_id=event.get("id"),
        **payload
    )
    fake_bookcall_db.append(new_call)
    # Send booking confirmation and lead notification emails
    try:
        send_booking_confirmation_with_zoho(
            client_name=data.name,
            client_email=data.email,
            call_datetime=data.preferred_datetime,
            provider=data.video_call_provider,
            call_link=meet_link,
            owner_email=None,
            client_message=data.message
        )
    except Exception as e:
        return {"message": f"Call booked but failed to send email: {str(e)}", "call": new_call, "success": False, "video_call_link": meet_link}
    # Save lead to database
    db_lead = Lead(name=data.name, email=data.email, interest=data.video_call_provider, message=data.message)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return {"message": "Call booked successfully.", "call": new_call, "lead": db_lead, "success": True, "video_call_link": meet_link}

@router.get("/bookings", response_model=List[BookCall], summary="List Booked Calls")
def list_booked_calls():
    return fake_bookcall_db

@router.post("/message", summary="Send Message")
def send_message(data: MessageCreate, db: Session = Depends(get_db)):
    missing = []
    if not data.name:
        missing.append("name")
    if not data.email:
        missing.append("email")
    if not data.message:
        missing.append("message")
    if missing:
        return {"message": f"Missing required fields: {', '.join(missing)}", "success": False}
    # Send contact message email
    try:
        send_contact_message_with_zoho(data.name, data.email, data.message, getattr(data, 'subject', None))
    except Exception as e:
        return {"message": f"Message saved but failed to send email: {str(e)}", "success": False}
    # Save lead to database only if not duplicate
    existing_lead = db.query(Lead).filter(Lead.email == data.email).first()
    if not existing_lead:
        db_lead = Lead(name=data.name, email=data.email, interest=None, message=data.message)
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
    return {"message": "Message sent successfully.", "success": True}

@router.get("/messages", response_model=List[Message], summary="List Messages")
def list_messages():
    return fake_message_db 