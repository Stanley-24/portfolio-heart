from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
from app.routes.auth import get_current_admin

router = APIRouter()

@router.post("/upload-thumbnail", summary="Upload project thumbnail/cover (admin only)")
def upload_project_thumbnail(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    upload_dir = "uploads/projects"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/uploads/projects/{file.filename}"} 