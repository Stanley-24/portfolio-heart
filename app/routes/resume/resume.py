from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.schemas.resume import ResumeStats as ResumeStatsSchema
from datetime import datetime
import os
from app.routes.auth import get_current_admin
from typing import Any
from app.models.resume import ResumeStats
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

RESUME_UPLOAD_PATH = "uploads/resume.pdf"

@router.post("/upload", summary="Upload Resume Pdf")
def upload_resume_pdf(file: UploadFile = File(...), admin: Any = Depends(get_current_admin)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    os.makedirs(os.path.dirname(RESUME_UPLOAD_PATH), exist_ok=True)
    try:
        with open(RESUME_UPLOAD_PATH, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    return {"message": "Resume PDF uploaded successfully.", "success": True}

@router.get("/file", summary="Get Resume Pdf")
def get_resume_pdf(db: Session = Depends(get_db)):
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    stats = db.query(ResumeStats).first()
    if not stats:
        stats = ResumeStats(downloads=0, views=1, last_download=None)
        db.add(stats)
    else:
        stats.views += 1
    db.commit()
    return FileResponse(RESUME_UPLOAD_PATH, media_type="application/pdf", filename="resume.pdf")

@router.delete("/", status_code=200, summary="Delete Resume")
def delete_resume(admin=Depends(get_current_admin)):
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    try:
        os.remove(RESUME_UPLOAD_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    return {"message": "Resume PDF deleted successfully.", "success": True}

@router.post("/save", summary="Save Resume Analytics")
def save_resume_analytics(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
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