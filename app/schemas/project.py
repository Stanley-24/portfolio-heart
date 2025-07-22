from pydantic import BaseModel, HttpUrl
from typing import List, Optional

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

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str

    class Config:
        from_attributes = True 