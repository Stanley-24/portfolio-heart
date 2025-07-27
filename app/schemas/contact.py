from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ContactMessageBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    subject: str = Field(..., max_length=255)
    message: str = Field(..., max_length=2000)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessageUpdate(ContactMessageBase):
    pass

class ContactMessageOut(ContactMessageBase):
    id: int
    is_read: bool = False
    is_replied: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    class Config:
        from_attributes = True 