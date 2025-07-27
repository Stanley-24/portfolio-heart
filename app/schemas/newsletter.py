from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class NewsletterBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

class NewsletterCreate(NewsletterBase):
    pass

class NewsletterUpdate(NewsletterBase):
    pass

class Newsletter(NewsletterBase):
    id: int
    subscribed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None

    class Config:
        from_attributes = True 