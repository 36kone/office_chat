import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    cellphone = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    password_recovery = Column(String, nullable=True)
    password_recovery_expire = Column(DateTime, nullable=True)
    single_session = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    online_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
