from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Experience(Base):
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL for current position
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=False)
    technologies = Column(Text, nullable=True)  # Comma-separated
    achievements = Column(Text, nullable=True)
    company_logo = Column(String(500), nullable=True)
    company_website = Column(String(500), nullable=True)
    icon = Column(String(50), nullable=True)  # Store the icon key
    color_scheme = Column(String(50), nullable=True)  # Store the color scheme
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Experience(id={self.id}, title='{self.title}', company='{self.company}')>" 