from pydantic import BaseModel, HttpUrl, validator, Field
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    description: str
    thumbnail: Optional[HttpUrl] = None
    technologies: List[str]
    githubUrl: Optional[str] = Field(None, alias="github_url")
    liveUrl: Optional[str] = Field(None, alias="live_url")
    featured: bool = False
    createdAt: Optional[str] = Field(None, alias="created_at")
    featuredAt: Optional[str] = None

    @validator("createdAt", "featuredAt", pre=True, always=True)
    def parse_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        if isinstance(v, str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
                except Exception:
                    continue
        raise ValueError("Date must be in YYYY-MM-DD format")

    class Config:
        allow_population_by_field_name = True
        from_attributes = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int  # Changed from str to int

    class Config:
        allow_population_by_field_name = True
        from_attributes = True 