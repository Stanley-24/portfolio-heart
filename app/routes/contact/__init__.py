from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.contact import ContactMessageCreate, ContactMessageOut
from app.models.contact import ContactMessage as ContactMessageModel
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from app.routes.auth import get_current_admin
import os
import smtplib
from email.message import EmailMessage

router = APIRouter()

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
    
    # Send email notification to owner
    send_contact_notification(data)
    
    # Send confirmation email to sender
    send_contact_confirmation(data)
    
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
    
    # Send call booking notification to owner
    send_call_booking_notification(data)
    
    # Send confirmation email to sender
    send_call_booking_confirmation(data)
    
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

# Email sending helpers
def send_contact_notification(data: ContactMessageCreate):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    owner_email = from_email
    
    subject = f"New Contact Message: {data.subject}"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>New Contact Message</h2>
        <div style='background:#f8f9fa;border-radius:6px;padding:16px;margin:16px 0;'>
          <p><strong>From:</strong> {data.name}</p>
          <p><strong>Email:</strong> {data.email}</p>
          <p><strong>Subject:</strong> {data.subject}</p>
          {data.phone and f'<p><strong>Phone:</strong> {data.phone}</p>' or ''}
          {data.company and f'<p><strong>Company:</strong> {data.company}</p>' or ''}
        </div>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:16px 0;'>
          <p><strong>Message:</strong></p>
          <p style='white-space:pre-wrap;'>{data.message}</p>
        </div>
      </div>
    </body></html>
    """
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = owner_email
    msg.set_content(f"New contact message from {data.name}: {data.message}")
    msg.add_alternative(html_content, subtype='html')
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

def send_contact_confirmation(data: ContactMessageCreate):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    
    subject = "Thank you for your message!"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>Thank you for your message!</h2>
        <p style='font-size:1.1em;color:#222;'>Hi {data.name},</p>
        <p style='font-size:1.1em;color:#222;'>Thank you for reaching out! I've received your message and will get back to you as soon as possible.</p>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:24px 0;'>
          <p style='margin:0;'><strong>Your message:</strong></p>
          <p style='white-space:pre-wrap;margin:8px 0 0 0;'>{data.message}</p>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Best regards,<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta</span>
        </p>
      </div>
    </body></html>
    """
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = data.email
    msg.set_content(f"Thank you for your message, {data.name}! I'll get back to you soon.")
    msg.add_alternative(html_content, subtype='html')
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

def send_call_booking_notification(data: ContactMessageCreate):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    owner_email = from_email
    
    subject = f"New Call Booking Request from {data.name}"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>New Call Booking Request</h2>
        <div style='background:#f8f9fa;border-radius:6px;padding:16px;margin:16px 0;'>
          <p><strong>From:</strong> {data.name}</p>
          <p><strong>Email:</strong> {data.email}</p>
          {data.phone and f'<p><strong>Phone:</strong> {data.phone}</p>' or ''}
          {data.company and f'<p><strong>Company:</strong> {data.company}</p>' or ''}
        </div>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:16px 0;'>
          <p><strong>Message:</strong></p>
          <p style='white-space:pre-wrap;'>{data.message}</p>
        </div>
      </div>
    </body></html>
    """
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = owner_email
    msg.set_content(f"New call booking request from {data.name}: {data.message}")
    msg.add_alternative(html_content, subtype='html')
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

def send_call_booking_confirmation(data: ContactMessageCreate):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    
    subject = "Call Booking Request Received!"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>Call Booking Request Received!</h2>
        <p style='font-size:1.1em;color:#222;'>Hi {data.name},</p>
        <p style='font-size:1.1em;color:#222;'>Thank you for your call booking request! I've received your message and will contact you soon to schedule our call.</p>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:24px 0;'>
          <p style='margin:0;'><strong>Your request:</strong></p>
          <p style='white-space:pre-wrap;margin:8px 0 0 0;'>{data.message}</p>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Best regards,<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta</span>
        </p>
      </div>
    </body></html>
    """
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = data.email
    msg.set_content(f"Thank you for your call booking request, {data.name}! I'll contact you soon to schedule our call.")
    msg.add_alternative(html_content, subtype='html')
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg) 