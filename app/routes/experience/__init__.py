from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
from app.schemas.experience import Experience, ExperienceCreate, ExperienceUpdate
from app.models.experience import Experience as ExperienceModel
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.routes.auth import get_current_admin
import uuid
from datetime import date
from dateutil.parser import parse as parse_date

router = APIRouter()

# Supported icon keys and their emoji
ICON_MAP = {
    "link": "🔗",
    "camera": "📸",
    "laptop": "💻",
    "star": "⭐",
    "rocket": "🚀",
    "paint": "🎨",
    "book": "📚"
}

def get_emoji(icon_key: str) -> str:
    if icon_key not in ICON_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported icon key: '{icon_key}'. Supported: {list(ICON_MAP.keys())}")
    return ICON_MAP[icon_key]

def db_to_api_exp(db_exp: ExperienceModel) -> Experience:
    # Convert DB model to API schema, including dateRange and icon mapping
    date_range = f"{db_exp.start_date.strftime('%b %Y')} - "
    if db_exp.is_current or db_exp.end_date is None:
        date_range += "Present"
    else:
        date_range += db_exp.end_date.strftime('%b %Y')
    return Experience(
        id=str(db_exp.id),
        dateRange=date_range,
        title=db_exp.title,
        company=db_exp.company,
        url=db_exp.company_website or "",
        icon=db_exp.icon if hasattr(db_exp, 'icon') and db_exp.icon else "laptop",
        colorScheme="",  # Set as needed
    )

@router.get("/", response_model=List[Experience], summary="List Experiences")
def list_experiences(db: Session = Depends(get_db)):
    db_experiences = db.query(ExperienceModel).all()
    result = []
    for db_exp in db_experiences:
        api_exp = db_to_api_exp(db_exp)
        api_exp.icon = get_emoji(api_exp.icon)
        result.append(api_exp)
    return result

@router.post("/", summary="Add Experience")
def create_experience(exp: ExperienceCreate, db: Session = Depends(get_db), admin: Any = Depends(get_current_admin)):
    print("USING FLEXIBLE DATE PARSING - create_experience")
    try:
        emoji = get_emoji(exp.icon)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    try:
        start_str, end_str = [s.strip() for s in exp.dateRange.split('-')]
        start_date = parse_date(start_str, default=date.today().replace(day=1)).date()
        if end_str.lower() in ["present", "now"]:
            end_date = None
            is_current = True
        else:
            end_date = parse_date(end_str, default=date.today().replace(day=1)).date()
            is_current = False
    except Exception as e:
        print(f"DATE PARSE ERROR: {e}")
        return {"message": f"Could not understand the date range you entered: '{exp.dateRange}'. Please try again.", "success": False}
    db_exp = ExperienceModel(
        title=exp.title,
        company=exp.company,
        location=None,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        description="",
        technologies="",
        achievements="",
        company_logo=None,
        company_website=exp.url,
    )
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    api_exp = db_to_api_exp(db_exp)
    api_exp.icon = emoji
    return {"message": "Experience created successfully.", "success": True, "experience": api_exp}

@router.put("/{exp_id}", summary="Update Experience")
def update_experience(exp_id: str, exp: ExperienceUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db_exp = db.query(ExperienceModel).filter(ExperienceModel.id == int(exp_id)).first()
    if not db_exp:
        return {"message": "Experience not found", "success": False}
    try:
        emoji = get_emoji(exp.icon)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    try:
        start_str, end_str = [s.strip() for s in exp.dateRange.split('-')]
        start_date = parse_date(start_str, default=date.today().replace(day=1)).date()
        if end_str.lower() in ["present", "now"]:
            end_date = None
            is_current = True
        else:
            end_date = parse_date(end_str, default=date.today().replace(day=1)).date()
            is_current = False
    except Exception:
        return {"message": "Invalid dateRange format. Please use a recognizable date format like 'Feb 2024 - Present' or '2024-02 - 2025-01'.", "success": False}
    db_exp.title = exp.title
    db_exp.company = exp.company
    db_exp.company_website = exp.url
    db_exp.start_date = start_date
    db_exp.end_date = end_date
    db_exp.is_current = is_current
    # db_exp.icon = exp.icon  # If you add icon to the DB model
    db.commit()
    db.refresh(db_exp)
    api_exp = db_to_api_exp(db_exp)
    api_exp.icon = emoji
    return {"message": "Experience updated successfully.", "success": True, "experience": api_exp}

@router.delete("/{exp_id}", status_code=200, summary="Delete Experience")
def delete_experience(exp_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db_exp = db.query(ExperienceModel).filter(ExperienceModel.id == int(exp_id)).first()
    if not db_exp:
        return {"message": "Experience not found", "success": False}
    db.delete(db_exp)
    db.commit()
    return {"message": "Experience deleted successfully.", "success": True} 