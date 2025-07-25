from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, LargeBinary, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    thumbnail = Column(String(500), nullable=True)
    short_description = Column(String(500), nullable=True)
    technologies = Column(JSON, nullable=True)  # Array of technologies
    image_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    featured = Column(Boolean, default=False)
    category = Column(String(100), nullable=True)  # e.g., "web", "mobile", "ai"
    difficulty = Column(String(50), nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    completion_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}')>" 

class ProjectThumbnail(Base):
    __tablename__ = "project_thumbnails"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 