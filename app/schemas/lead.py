from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LeadCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    email: Optional[EmailStr] = None
    interest: str = Field(..., max_length=512)

class LeadOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[EmailStr]
    interest: str
    created_at: datetime

    class Config:
        orm_mode = True 