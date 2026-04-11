from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict

from app.schemas import BaseSchema, TimestampedResponse


class CreateSessionSchema(BaseSchema):
    user_id: UUID | None = None
    expire_at: datetime | None = None
    user_device: str | None = None
    revoked_at: datetime | None = None


class UserSessionSearchRequest(BaseSchema):
    keyword: str | None = None
    size: int = 10
    page: int = 1


class UserSessionResponse(TimestampedResponse):
    id: UUID
    user_id: UUID | None = None
    expire_at: datetime | None = None
    user_device: str | None = None
    revoked_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserSessionUpdate(BaseSchema, TimestampedResponse):
    id: UUID
    expire_at: datetime | None = None
    user_agent: str | None = None
    revoked_at: datetime | None = None
    ipv4: str | None = None
    ipv6: str | None = None
