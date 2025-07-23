from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.contact import Lead
from app.schemas.lead import LeadCreate, LeadOut
from app.routes.auth import get_current_admin
from typing import List

router = APIRouter()

@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = Lead(name=lead.name, email=lead.email, interest=lead.interest)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/leads", response_model=List[LeadOut])
def get_all_leads(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.delete("/leads/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return

@router.patch("/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, lead_update: LeadCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in lead_update.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead 