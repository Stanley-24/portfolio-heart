from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
import os
from app.routes.auth import get_current_admin
from app.models.project import Project
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.post("/upload-thumbnail", summary="Upload project thumbnail/cover (admin only)")
def upload_project_thumbnail(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    upload_dir = "uploads/projects"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    url = f"/uploads/projects/{file.filename}"

    # Update the project in the database
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.thumbnail = url
    db.commit()
    db.refresh(project)

    return {"url": url, "project": {"id": project.id, "thumbnail": project.thumbnail}} 