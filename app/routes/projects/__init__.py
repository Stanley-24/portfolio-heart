from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Any
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
import uuid
from app.routes.auth import get_current_admin
import os
from .upload_thumbnail import router as upload_thumbnail_router

router = APIRouter()

# Fake in-memory DB
fake_project_db = []

# Helper: validate project fields
def validate_project(data: ProjectCreate):
    if not data.title or not data.description or not data.thumbnail or not data.technologies or not data.githubUrl or not data.liveUrl or not data.createdAt:
        raise HTTPException(status_code=400, detail="All fields except featuredAt are required.")
    if not isinstance(data.technologies, list) or len(data.technologies) == 0:
        raise HTTPException(status_code=400, detail="At least one technology is required.")

@router.get("/", response_model=List[Project], summary="List Projects")
def list_projects():
    """List up to 6 valid projects, featured first, sorted as frontend expects."""
    # Filter valid projects
    valid_projects = [p for p in fake_project_db if p.title and p.description and p.thumbnail and p.technologies and len(p.technologies) > 0 and p.githubUrl and p.liveUrl]
    # Sort: featured first (by featuredAt desc), then non-featured (by createdAt desc)
    sorted_projects = sorted(valid_projects, key=lambda p: (
        not p.featured,  # featured first
        str(p.featuredAt or ''),  # newest featuredAt first
        str(p.createdAt)
    ), reverse=True)
    return sorted_projects[:6]

@router.post("/", summary="Add Project")
def create_project(data: ProjectCreate, admin: Any = Depends(get_current_admin)):
    validate_project(data)
    new_id = str(uuid.uuid4())
    new_project = Project(id=new_id, **data.model_dump())
    fake_project_db.append(new_project)
    return {"message": "Project created successfully.", "success": True, "project": new_project}

@router.put("/{project_id}", summary="Update Project")
def update_project(project_id: str, data: ProjectUpdate, admin=Depends(get_current_admin)):
    try:
        validate_project(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    for i, old_project in enumerate(fake_project_db):
        if old_project.id == project_id:
            updated_project = Project(id=project_id, **data.model_dump())
            fake_project_db[i] = updated_project
            return {"message": "Project updated successfully.", "success": True, "project": updated_project}
    return {"message": "Project not found", "success": False}

@router.delete("/{project_id}", status_code=200, summary="Delete Project")
def delete_project(project_id: str, admin=Depends(get_current_admin)):
    for i, project in enumerate(fake_project_db):
        if project.id == project_id:
            del fake_project_db[i]
            return {"message": "Project deleted successfully.", "success": True}
    return {"message": "Project not found", "success": False}

router.include_router(upload_thumbnail_router) 