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
def validate_project(data: ProjectCreate):
    if not data.title or not data.description or not data.technologies:
        raise HTTPException(status_code=400, detail="Title, description, and technologies are required.")
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
    base_url = "https://portfolio-heart.onrender.com"
    for project in projects:
        if project.thumbnail and not project.thumbnail.startswith("http"):
            project.thumbnail = f"{base_url}{project.thumbnail}"
    return projects

@router.post("/", summary="Add Project")
def create_project(data: ProjectCreate, db: Session = Depends(get_db), admin: Any = Depends(get_current_admin)):
    print(f"[DEBUG] Received project data: {data}")
    print(f"[DEBUG] Data model dump: {data.model_dump()}")
    try:
        validate_project(data)
        snake_data = camel_to_snake(data.model_dump())
        print(f"[DEBUG] Snake case data: {snake_data}")
        new_project = Project(**{k: v for k, v in snake_data.items() if v is not None})
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {"message": "Project created successfully.", "success": True, "project": new_project}
    except HTTPException as e:
        print(f"[DEBUG] HTTP Exception: {str(e)}")
        raise e
    except Exception as e:
        print(f"[DEBUG] Error creating project: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to create project: {str(e)}")

@router.put("/{project_id}", summary="Update Project")
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    print(f"[DEBUG] Updating project {project_id}")
    print(f"[DEBUG] Received update data: {data}")
    print(f"[DEBUG] Data model dump: {data.model_dump()}")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"message": "Project not found", "success": False}
    
    snake_data = camel_to_snake(data.model_dump(exclude_unset=True))
    print(f"[DEBUG] Snake case data: {snake_data}")
    
    for key, value in snake_data.items():
        if value is not None:
            print(f"[DEBUG] Setting {key} = {value}")
            setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    print(f"[DEBUG] Updated project: {project.github_url}, {project.live_url}")
    return {"message": "Project updated successfully.", "success": True, "project": project}

@router.delete("/{project_id}", status_code=200, summary="Delete Project")
def delete_project(project_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    print(f"[DEBUG] Deleting project {project_id}")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        print(f"[DEBUG] Project {project_id} not found")
        return {"message": "Project not found", "success": False}
    
    print(f"[DEBUG] Found project: {project.title}")
    db.delete(project)
    db.commit()
    print(f"[DEBUG] Project {project_id} deleted successfully")
    return {"message": "Project deleted successfully.", "success": True} 