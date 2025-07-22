from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<NewsletterSubscriber(id={self.id}, email='{self.email}')>" 