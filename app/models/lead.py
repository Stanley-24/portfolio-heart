from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=True)
    email = Column(String(256), nullable=True)
    interest = Column(String(512), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 