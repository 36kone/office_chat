import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    is_group = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("ChatUser", back_populates="chat", cascade="all, delete-orphan", lazy="noload")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan", lazy="noload")
