from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name='{self.name}', email='{self.email}')>" 

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    interest = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatbotReply(Base):
    __tablename__ = "chatbot_replies"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    sender = Column(String(50), nullable=False)  # 'bot' or 'recruiter'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatbotReply(id={self.id}, sender='{self.sender}')>" 