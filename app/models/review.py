from sqlalchemy import Column, Integer, String, Text, DateTime, Integer as Rating, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=False)
    client_title = Column(String(255), nullable=True)
    client_company = Column(String(255), nullable=True)
    client_avatar = Column(String(500), nullable=True)
    rating = Column(Rating, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=False)
    project_type = Column(String(100), nullable=True)  # e.g., "web development", "consulting"
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)  # New approval status field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Review(id={self.id}, client='{self.client_name}', rating={self.rating})>" 