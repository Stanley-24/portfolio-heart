from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.email_service import send_resume_with_zoho
import os

class EmailRequest(BaseModel):
    email: str

router = APIRouter()

@router.post("/send_resume")
def send_resume(request: EmailRequest):
    email = request.email
    resume_path = "uploads/resume.pdf"
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume not found.")
    try:
        send_resume_with_zoho(email, resume_path)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 