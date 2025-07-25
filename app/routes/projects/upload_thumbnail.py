from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Response
import os
from app.routes.auth import get_current_admin
from app.models.project import Project, ProjectThumbnail
from sqlalchemy.orm import Session
from app.core.database import get_db
import unicodedata

router = APIRouter()

def sanitize_filename(filename):
    return unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

@router.post("/upload-thumbnail", summary="Upload project thumbnail/cover (admin only)")
def upload_project_thumbnail(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    image_bytes = file.file.read()
    filename = file.filename

    # Save to ProjectThumbnail table (overwrite if exists)
    thumbnail = db.query(ProjectThumbnail).filter(ProjectThumbnail.project_id == project_id).first()
    if not thumbnail:
        thumbnail = ProjectThumbnail(project_id=project_id, filename=filename, image_data=image_bytes)
        db.add(thumbnail)
    else:
        thumbnail.filename = filename
        thumbnail.image_data = image_bytes
    db.commit()
    db.refresh(thumbnail)

    # Optionally update the project.thumbnail field to a new endpoint
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.thumbnail = f"/api/projects/{project_id}/thumbnail"
    db.commit()
    db.refresh(project)

    return {"url": project.thumbnail, "project": {"id": project.id, "thumbnail": project.thumbnail}}

@router.get("/{project_id}/thumbnail", summary="Get project thumbnail image")
def get_project_thumbnail(project_id: int, db: Session = Depends(get_db)):
    thumbnail = db.query(ProjectThumbnail).filter(ProjectThumbnail.project_id == project_id).first()
    if not thumbnail or not thumbnail.image_data:
        raise HTTPException(status_code=404, detail="Thumbnail not found for this project.")
    safe_filename = sanitize_filename(thumbnail.filename)
    return Response(thumbnail.image_data, media_type="image/png", headers={"Content-Disposition": f"inline; filename={safe_filename}"}) 