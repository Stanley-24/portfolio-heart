from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ReviewBase(BaseModel):
    name: str
    review: str
    avatarUrl: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    pass

class Review(ReviewBase):
    id: str

    class Config:
        from_attributes = True 