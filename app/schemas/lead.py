from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LeadCreate(BaseModel):
    name: str = Field(..., max_length=128)
    email: EmailStr
    interest: str = Field(..., max_length=512)

class LeadOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[EmailStr]
    interest: str
    created_at: datetime

    class Config:
        from_attributes = True 