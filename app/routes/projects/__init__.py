from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Any
from app.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate
from app.models.project import Project
from app.core.database import get_db
from sqlalchemy.orm import Session
import uuid
from app.routes.auth import get_current_admin
import os
from .upload_thumbnail import router as upload_thumbnail_router

router = APIRouter()
router.include_router(upload_thumbnail_router)

# Helper: validate project fields
# (You may want to keep or update this for extra validation)
def validate_project(data: ProjectCreate):
    if not data.title or not data.description or not data.thumbnail or not data.technologies or not data.githubUrl or not data.liveUrl or not data.createdAt:
        raise HTTPException(status_code=400, detail="All fields except featuredAt are required.")
    if not isinstance(data.technologies, list) or len(data.technologies) == 0:
        raise HTTPException(status_code=400, detail="At least one technology is required.")

def camel_to_snake(data):
    def to_str(val):
        return str(val) if val is not None else None
    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "thumbnail": to_str(data.get("thumbnail")),
        "short_description": data.get("shortDescription"),
        "technologies": data.get("technologies"),
        "image_url": to_str(data.get("imageUrl")),
        "github_url": to_str(data.get("githubUrl")),
        "live_url": to_str(data.get("liveUrl")),
        "demo_url": to_str(data.get("demoUrl")),
        "featured": data.get("featured"),
        "category": data.get("category"),
        "difficulty": data.get("difficulty"),
        "completion_date": data.get("completionDate"),
        "created_at": data.get("createdAt"),
        # Add more mappings as needed
    }

@router.get("/", response_model=List[ProjectSchema], summary="List Projects")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

@router.post("/", summary="Add Project")
def create_project(data: ProjectCreate, db: Session = Depends(get_db), admin: Any = Depends(get_current_admin)):
    validate_project(data)
    snake_data = camel_to_snake(data.model_dump())
    new_project = Project(**{k: v for k, v in snake_data.items() if v is not None})
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": "Project created successfully.", "success": True, "project": new_project}

@router.put("/{project_id}", summary="Update Project")
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"message": "Project not found", "success": False}
    snake_data = camel_to_snake(data.model_dump(exclude_unset=True))
    for key, value in snake_data.items():
        if value is not None:
            setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return {"message": "Project updated successfully.", "success": True, "project": project}

@router.delete("/{project_id}", status_code=200, summary="Delete Project")
def delete_project(project_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"message": "Project not found", "success": False}
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully.", "success": True} 