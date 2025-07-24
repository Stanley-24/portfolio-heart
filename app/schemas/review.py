from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ReviewBase(BaseModel):
    client_name: str
    review_text: str
    client_avatar: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int

    class Config:
        from_attributes = True 