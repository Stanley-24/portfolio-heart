from pydantic import BaseModel, EmailStr
from typing import Optional

class BookCallBase(BaseModel):
    name: str
    email: EmailStr
    preferred_datetime: str
    message: Optional[str] = None
    video_call_provider: str
    video_call_link: Optional[str] = None  # Will be empty for now

class BookCallCreate(BookCallBase):
    pass

class BookCall(BookCallBase):
    id: str
    contacted_at: str
    calendar_event_id: Optional[str] = None

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    name: str
    email: EmailStr
    message: str
    subject: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    sent_at: str

    class Config:
        from_attributes = True 