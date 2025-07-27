from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import Response
from app.schemas.resume import ResumeStats as ResumeStatsSchema, Resume as ResumeSchema
from datetime import datetime
from app.routes.auth import get_current_admin
from typing import Any, List
from app.models.resume import ResumeStats, Resume
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/upload", summary="Upload Resume Pdf")
def upload_resume_pdf(file: UploadFile = File(...), db: Session = Depends(get_db), admin: Any = Depends(get_current_admin)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    pdf_bytes = file.file.read()
    # Save to database only
    resume = db.query(Resume).first()
    if not resume:
        resume = Resume(pdf_data=pdf_bytes, name="Stanley Owarieta", title="Software Engineer", email="", phone="", location="", summary="")
        db.add(resume)
    else:
        resume.pdf_data = pdf_bytes
    db.commit()
    return {"message": "Resume PDF uploaded and saved to database.", "success": True}

@router.get("/file", summary="Get Resume Pdf")
def get_resume_pdf(db: Session = Depends(get_db)):
    resume = db.query(Resume).first()
    if not resume or not resume.pdf_data:
        raise HTTPException(status_code=404, detail="Resume PDF not found in database.")
    stats = db.query(ResumeStats).first()
    if not stats:
        stats = ResumeStats(downloads=0, views=1, last_download=None)
        db.add(stats)
    else:
        stats.views += 1
    db.commit()
    return Response(resume.pdf_data, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=resume.pdf"})

@router.delete("/", status_code=200, summary="Delete Resume")
def delete_resume(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    resume = db.query(Resume).first()
    if not resume or not resume.pdf_data:
        raise HTTPException(status_code=404, detail="Resume PDF not found in database.")
    resume.pdf_data = None
    db.commit()
    return {"message": "Resume PDF deleted from database.", "success": True}

@router.post("/save", summary="Save Resume Analytics")
def save_resume_analytics(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    resume = db.query(Resume).first()
    if not resume or not resume.pdf_data:
        raise HTTPException(status_code=404, detail="Resume PDF not found in database.")
    stats = db.query(ResumeStats).first()
    if not stats:
        stats = ResumeStats(downloads=1, views=0, last_download=datetime.utcnow())
        db.add(stats)
    else:
        stats.downloads += 1
        stats.last_download = datetime.utcnow()
    db.commit()
    return {"message": "Analytics saved", "success": True}

@router.get("/stats", response_model=ResumeStatsSchema, summary="Get Resume Stats")
def get_resume_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    stats = db.query(ResumeStats).first()
    if not stats:
        stats = ResumeStats(downloads=0, views=0, last_download=None)
        db.add(stats)
        db.commit()
    return stats

@router.get("/", response_model=List[ResumeSchema], summary="List All Resumes")
def list_resumes(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Get all resumes (admin only)"""
    return db.query(Resume).all()

@router.get("/info", response_model=ResumeSchema, summary="Get Resume Info")
def get_resume_info(db: Session = Depends(get_db)):
    """Get resume information (public)"""
    resume = db.query(Resume).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume

@router.put("/info", summary="Update Resume Info")
def update_resume_info(resume_data: ResumeSchema, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    """Update resume information (admin only)"""
    resume = db.query(Resume).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    
    for key, value in resume_data.model_dump(exclude_unset=True).items():
        if key != 'id':  # Don't update the ID
            setattr(resume, key, value)
    
    db.commit()
    db.refresh(resume)
    return {"message": "Resume information updated successfully.", "success": True, "resume": resume} 