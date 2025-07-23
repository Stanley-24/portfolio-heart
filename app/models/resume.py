from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Resume(Base):
    __tablename__ = "resume"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)
    portfolio = Column(String(500), nullable=True)
    github = Column(String(500), nullable=True)
    linkedin = Column(String(500), nullable=True)
    twitter = Column(String(500), nullable=True)
    summary = Column(Text, nullable=False)
    skills = Column(JSON, nullable=True)  # Store as JSON array
    experience = Column(JSON, nullable=True)  # Store as JSON array
    projects = Column(JSON, nullable=True)  # Store as JSON array
    education = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Resume(id={self.id}, name='{self.name}')>" 

class ResumeStats(Base):
    __tablename__ = "resume_stats"
    id = Column(Integer, primary_key=True, index=True)
    downloads = Column(Integer, default=0)
    views = Column(Integer, default=0)
    last_download = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 