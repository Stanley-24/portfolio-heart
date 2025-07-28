from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.contact import ContactMessageCreate, ContactMessageOut
from app.models.contact import ContactMessage as ContactMessageModel
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from app.routes.auth import get_current_admin
from app.services.email_service import (
    send_admin_contact_notification,
    send_admin_booking_notification,
    send_contact_message_with_zoho,
    send_booking_confirmation_with_zoho
)
import os

router = APIRouter()

# Admin email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "owarieta24@gmail.com")

@router.post("/send-message", summary="Send Contact Message")
def send_contact_message(data: ContactMessageCreate, db: Session = Depends(get_db)):
    """Send a contact message and save to database"""
    # Save to database
    db_message = ContactMessageModel(
        name=data.name,
        email=data.email,
        subject=data.subject,
        message=data.message,
        phone=data.phone,
        company=data.company
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send admin notification
    try:
        send_admin_contact_notification(ADMIN_EMAIL, {
            'name': data.name,
            'email': data.email,
            'subject': data.subject,
            'message': data.message,
            'phone': data.phone,
            'company': data.company
        })
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    # Send confirmation email to sender
    try:
        send_contact_message_with_zoho(data.name, data.email, data.message, data.subject)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
    
    return {"message": "Message sent successfully", "success": True}

@router.post("/book-call", summary="Book a Call")
def book_call(data: ContactMessageCreate, db: Session = Depends(get_db)):
    """Book a call and save to database"""
    # Save to database with call booking subject
    db_message = ContactMessageModel(
        name=data.name,
        email=data.email,
        subject="Call Booking Request",
        message=f"Call booking request from {data.name}\n\nMessage: {data.message}\nPhone: {data.phone or 'Not provided'}\nCompany: {data.company or 'Not provided'}",
        phone=data.phone,
        company=data.company
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send admin notification
    try:
        send_admin_booking_notification(ADMIN_EMAIL, {
            'name': data.name,
            'email': data.email,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'provider': 'Google Meet',
            'message': data.message
        })
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    # Send confirmation email to sender
    try:
        send_booking_confirmation_with_zoho(
            data.name, 
            data.email, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Google Meet',
            'https://meet.google.com/xxx-xxxx-xxx',
            ADMIN_EMAIL,
            data.message
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
    
    return {"message": "Call booking request sent successfully", "success": True}

@router.get("/admin", response_model=List[ContactMessageOut], summary="Get All Contact Messages (Admin)")
def get_all_messages(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Get all contact messages (admin only)"""
    return db.query(ContactMessageModel).order_by(ContactMessageModel.created_at.desc()).all()

@router.get("/admin/{message_id}", response_model=ContactMessageOut, summary="Get Contact Message (Admin)")
def get_message(message_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Get a specific contact message (admin only)"""
    message = db.query(ContactMessageModel).filter(ContactMessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.delete("/admin/{message_id}", summary="Delete Contact Message (Admin)")
def delete_message(message_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Delete a contact message (admin only)"""
    message = db.query(ContactMessageModel).filter(ContactMessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully", "success": True}

@router.patch("/admin/{message_id}/mark-read", summary="Mark Message as Read (Admin)")
def mark_as_read(message_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Mark a message as read (admin only)"""
    message = db.query(ContactMessageModel).filter(ContactMessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    return {"message": "Message marked as read", "success": True} 