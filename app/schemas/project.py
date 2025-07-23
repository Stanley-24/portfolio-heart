from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    description: str
    thumbnail: HttpUrl
    technologies: List[str]
    githubUrl: HttpUrl
    liveUrl: HttpUrl
    featured: bool = False
    createdAt: str
    featuredAt: Optional[str] = None

    @validator("createdAt", "featuredAt", pre=True, always=True)
    def parse_dates(cls, v):
        if v is None:
            return v
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        raise ValueError("Date must be in YYYY-MM-DD format")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str

    class Config:
        from_attributes = True 