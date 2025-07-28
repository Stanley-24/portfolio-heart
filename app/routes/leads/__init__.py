from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.contact import Lead
from app.core.database import get_db
from app.services.email_service import send_admin_lead_notification
from sqlalchemy.orm import Session
import os

router = APIRouter()

# Admin email configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "owarieta24@gmail.com")

@router.post("/", summary="Add Lead")
def create_lead(name: str, email: str, interest: str = None, message: str = None, db: Session = Depends(get_db)):
    lead = Lead(name=name, email=email, interest=interest, message=message)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Send admin notification
    try:
        send_admin_lead_notification(ADMIN_EMAIL, {
            'name': name,
            'email': email,
            'company': interest,  # Using interest as company
            'source': 'Portfolio Website',
            'message': message or 'No message provided'
        })
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    return {"message": "Lead created successfully.", "success": True, "lead": lead}

@router.get("/", response_model=List[dict], summary="List Leads")
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return [lead.__dict__ for lead in leads] 