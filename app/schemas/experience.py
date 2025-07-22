from pydantic import BaseModel
from typing import Optional

class ExperienceBase(BaseModel):
    dateRange: str
    title: str
    company: str
    url: str
    icon: str
    colorScheme: str

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceUpdate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: str

    class Config:
        from_attributes = True 