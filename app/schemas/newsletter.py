from pydantic import BaseModel, EmailStr
from typing import Optional

class NewsletterBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    subscribed_at: Optional[str] = None
    unsubscribed_at: Optional[str] = None

class NewsletterCreate(NewsletterBase):
    pass

class NewsletterUpdate(NewsletterBase):
    pass

class Newsletter(NewsletterBase):
    id: str

    class Config:
        from_attributes = True 