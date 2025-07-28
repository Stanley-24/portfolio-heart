from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.newsletter import Newsletter, NewsletterCreate, NewsletterUpdate
from app.models.newsletter import NewsletterSubscriber
from app.core.database import get_db
from app.core.analytics import analytics_tracker
from app.services.email_service import send_admin_newsletter_notification
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.routes.auth import get_current_admin
import os
import smtplib
from email.message import EmailMessage

router = APIRouter()

# Admin email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "owarieta24@gmail.com")

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
    
    # Get total subscriber count for admin notification
    total_subscribers = db.query(NewsletterSubscriber).count()
    
    # Track conversion for analytics
    analytics_tracker.track_conversion(
        conversion_type="newsletter_signup",
        user_ip="unknown",  # Will be set by middleware
        user_agent="unknown",  # Will be set by middleware
        metadata={
            "email": data.email,
            "total_subscribers": total_subscribers
        }
    )
    
    # Send welcome email to client
    send_newsletter_welcome_email(data.email)
    
    # Send admin notification
    try:
        send_admin_newsletter_notification(ADMIN_EMAIL, {
            'email': data.email,
            'total_subscribers': total_subscribers
        })
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    return {"message": "Subscribed successfully.", "success": True, "subscriber": {"email": new_sub.email}}

@router.get("/admin", response_model=List[Newsletter], summary="Get All Newsletter Subscribers (Admin)")
def get_all_subscribers(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Get all newsletter subscribers (admin only)"""
    return db.query(NewsletterSubscriber).order_by(NewsletterSubscriber.subscribed_at.desc()).all()

@router.delete("/admin/{subscriber_id}", summary="Delete Newsletter Subscriber (Admin)")
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Delete a newsletter subscriber (admin only)"""
    subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    db.delete(subscriber)
    db.commit()
    return {"message": "Subscriber deleted successfully", "success": True}

@router.get("/admin/stats", summary="Get Newsletter Statistics (Admin)")
def get_newsletter_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Get newsletter statistics (admin only)"""
    total_subscribers = db.query(NewsletterSubscriber).count()
    active_subscribers = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.is_active == True).count()
    
    # Get recent subscribers (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_subscribers = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.subscribed_at >= week_ago
    ).count()
    
    return {
        "total_subscribers": total_subscribers,
        "active_subscribers": active_subscribers,
        "recent_subscribers": recent_subscribers
    }

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
    owner_email = ADMIN_EMAIL
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