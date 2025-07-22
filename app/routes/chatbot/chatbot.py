from fastapi import APIRouter, HTTPException, Depends
from app.services.openai_service import get_openai_response
from app.core.database import get_db
from sqlalchemy.orm import Session
import requests
import os
from pydantic import BaseModel

router = APIRouter()

def format_experience(experience_list):
    if not isinstance(experience_list, list):
        return "No experience data available."
    return "\n".join(
        f"- {exp.get('title', 'Role')} at {exp.get('company', 'Company')} ({exp.get('start_date', 'N/A')}–{exp.get('end_date', 'Present')}): {exp.get('description', '')[:100]}..."
        for exp in experience_list[:3]
    )

def format_projects(projects_list):
    if not isinstance(projects_list, list):
        return "No project data available."
    return "\n".join(
        f"- {proj.get('name', 'Project')}: {proj.get('description', '')[:100]}... (Tech: {', '.join(proj.get('technologies', []))})"
        for proj in projects_list[:3]
    )

# Add your dynamic context here
SKILLS = "Python, JavaScript, TypeScript, React, Next.js, Tailwind CSS, FastAPI, PostgreSQL, REST APIs, Docker, CI/CD"
LOCATION = "Lagos, Nigeria (open to remote and international opportunities)"
AVAILABILITY = "Actively seeking new full-time or contract roles. Available immediately."
LINKS = (
    "Portfolio: https://stanley-o.vercel.app/\n"
    "GitHub: https://github.com/Stanley-24\n"
    "LinkedIn: https://www.linkedin.com/in/stanley-owarieta/\n"
    "Blog: https://stanley-dev.hashnode.dev/\n"
    "Resume: http://localhost:8000/resume/file"
    "X: https://x.com/Stanley_24_"
)

SYSTEM_PROMPT = (
    "You are Stanley Owarieta’s professional assistant. Always answer as if you are helping a recruiter or hiring manager learn about Stanley’s experience, skills, and availability. Use the provided context. Be concise, friendly, and highlight Stanley’s strengths as a full stack engineer and team player. If you don’t know something, say so politely. Always offer to share Stanley’s resume or contact details if appropriate."
)

class ChatbotRequest(BaseModel):
    message: str

@router.post("/chatbot")
def chatbot_endpoint(request: ChatbotRequest, db: Session = Depends(get_db)):
    message = request.message
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    try:
        exp_resp = requests.get(f"{backend_url}/api/experience", timeout=5)
        proj_resp = requests.get(f"{backend_url}/api/projects", timeout=5)
        experience = exp_resp.json() if exp_resp.ok else []
        projects = proj_resp.json() if proj_resp.ok else []
    except Exception:
        experience = []
        projects = []

    if not experience:
        experience = [{"title": "Full Stack Engineer", "company": "N/A", "start_date": "N/A", "description": "Stanley is a skilled engineer with experience in Python, JavaScript, React, FastAPI, and PostgreSQL."}]
    if not projects:
        projects = [{"name": "PhotoPilot", "description": "A photo management and sharing platform.", "technologies": ["React", "FastAPI"]}]

    exp_summary = format_experience(experience)
    proj_summary = format_projects(projects)

    # Build the full context
    context = (
        f"Experience:\n{exp_summary}\n\n"
        f"Projects:\n{proj_summary}\n\n"
        f"Skills: {SKILLS}\n"
        f"Location: {LOCATION}\n"
        f"Availability: {AVAILABILITY}\n"
        f"Links: {LINKS}\n"
    )

    try:
        answer = get_openai_response(message, context, SYSTEM_PROMPT)
        return {"answer": answer}
    except Exception:
        return {"answer": "Sorry, I'm unable to answer complex questions right now, but you can ask about Stanley’s projects, skills, or contact options!"} 