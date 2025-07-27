from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.newsletter import Newsletter, NewsletterCreate, NewsletterUpdate
from app.models.newsletter import NewsletterSubscriber
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from app.routes.auth import get_current_admin
import os
import smtplib
from email.message import EmailMessage

router = APIRouter()

# Helper: validate newsletter fields
def validate_newsletter(data: NewsletterCreate):
    if not data.email:
        raise HTTPException(status_code=400, detail="Email is required.")

@router.post("/subscribe", summary="Subscribe to Newsletter")
def subscribe_newsletter(data: NewsletterCreate, db: Session = Depends(get_db)):
        validate_newsletter(data)
    # Prevent duplicate emails
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == data.email).first()
    if existing:
            return {"message": "Email already subscribed.", "success": False}
    new_sub = NewsletterSubscriber(email=data.email, is_active=True, subscribed_at=datetime.utcnow())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    # Send welcome email to client
    send_newsletter_welcome_email(data.email)
    # Send lead notification to owner
    send_newsletter_lead_notification(data.email)
    return {"message": "Subscribed successfully.", "success": True, "subscriber": {"email": new_sub.email}}

# Email sending helpers
def send_newsletter_welcome_email(email):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    subject = "Welcome to Stanley's Newsletter!"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>Welcome to Stanley's Newsletter!</h2>
        <p style='font-size:1.1em;color:#222;'>Hi there,<br/>
          Thank you for subscribing to Stanley's newsletter! You'll now receive updates, tips, and news straight to your inbox.</p>
        <div style='background:#f1f5f9;border-radius:6px;padding:16px;margin:24px 0;'>
          <b style='color:#2563eb;'>If you have any questions or want to unsubscribe, just reply to this email.</b>
        </div>
        <p style='margin-top:2em;font-size:1em;color:#444;'>
          Best,<br/>
          <span style='color:#2563eb;font-weight:bold;'>Stanley Owarieta</span>
        </p>
      </div>
    </body></html>
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = email
    msg.set_content("Thank you for subscribing to Stanley's newsletter!")
    msg.add_alternative(html_content, subtype='html')
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

def send_newsletter_lead_notification(email):
    smtp_server = os.getenv("ZOHO_SMTP_SERVER")
    smtp_port = int(os.getenv("ZOHO_SMTP_PORT", 465))
    smtp_user = os.getenv("ZOHO_SMTP_USER")
    smtp_pass = os.getenv("ZOHO_SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM")
    owner_email = from_email
    subject = "New Newsletter Subscriber"
    html_content = f"""
    <html><body style='font-family:Segoe UI,Arial,sans-serif;background:#f9f9fb;padding:0;margin:0;'>
      <div style='max-width:520px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px #e3e8f0;padding:32px;'>
        <h2 style='color:#2563eb;margin-bottom:8px;'>New Newsletter Subscriber</h2>
        <ul style='color:#222;font-size:1.05em;'>
          <li><b>Email:</b> {email}</li>
        </ul>
      </div>
    </body></html>
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = owner_email
    msg.set_content(f"A new subscriber has joined your newsletter: {email}")
    msg.add_alternative(html_content, subtype='html')
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg) 