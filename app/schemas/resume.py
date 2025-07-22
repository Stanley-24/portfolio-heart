from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    name: str
    title: str
    email: EmailStr
    phone: str
    location: str
    portfolio: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    summary: str
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ResumeStats(BaseModel):
    downloads: int
    views: int
    last_download: Optional[datetime] = None
    success: bool = True 