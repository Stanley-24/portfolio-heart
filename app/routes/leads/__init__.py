from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.contact import Lead
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", summary="Add Lead")
def create_lead(name: str, email: str, interest: str = None, message: str = None, db: Session = Depends(get_db)):
    lead = Lead(name=name, email=email, interest=interest, message=message)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"message": "Lead created successfully.", "success": True, "lead": lead}

@router.get("/", response_model=List[dict], summary="List Leads")
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return [lead.__dict__ for lead in leads] 