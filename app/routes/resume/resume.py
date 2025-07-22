from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.schemas.resume import ResumeStats
from datetime import datetime
import os
from app.routes.auth import get_current_admin
from typing import Any

router = APIRouter()

# In-memory fake stats
fake_stats = {"downloads": 0, "views": 0, "last_download": None}
RESUME_UPLOAD_PATH = "uploads/resume.pdf"

@router.post("/upload", summary="Upload Resume Pdf")
def upload_resume_pdf(file: UploadFile = File(...), admin: Any = Depends(get_current_admin)):
    """Upload a PDF resume file."""
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
def get_resume_pdf():
    """Download or view the uploaded resume PDF file."""
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    fake_stats["views"] += 1
    return FileResponse(RESUME_UPLOAD_PATH, media_type="application/pdf", filename="resume.pdf")

@router.delete("/", status_code=200, summary="Delete Resume")
def delete_resume(admin=Depends(get_current_admin)):
    """Delete the resume PDF file."""
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    try:
        os.remove(RESUME_UPLOAD_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    return {"message": "Resume PDF deleted successfully.", "success": True}

@router.post("/save", summary="Save Resume Analytics")
def save_resume_analytics(admin=Depends(get_current_admin)):
    """Increment download analytics for the resume."""
    if not os.path.exists(RESUME_UPLOAD_PATH):
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    fake_stats["downloads"] += 1
    fake_stats["last_download"] = datetime.utcnow()
    return {"message": "Analytics saved", "success": True}

@router.get("/stats", response_model=ResumeStats, summary="Get Resume Stats")
def get_resume_stats(admin=Depends(get_current_admin)):
    """Get analytics stats for the resume."""
    # Always include 'success': True in the response
    stats = dict(fake_stats) if fake_stats else {"downloads": 0, "views": 0, "last_download": None}
    stats["success"] = True
    return stats 