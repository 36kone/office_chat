from uuid import UUID

from pydantic import ConfigDict, EmailStr

from ..base import BaseSchema, TimestampedResponse


class CreateUser(BaseSchema):
    name: str
    email: EmailStr
    password: str
    cellphone: str | None = None
    single_session: bool = True
    is_admin: bool = False


class UserResponse(BaseSchema, TimestampedResponse):
    id: UUID
    name: str
    email: EmailStr
    cellphone: str | None = None
    single_session: bool = True

    model_config = ConfigDict(from_attributes=True)


class SimpleUserResponse(BaseSchema):
    id: UUID
    name: str
    email: EmailStr
    is_admin: bool


class UpdateUser(BaseSchema):
    id: UUID
    name: str | None = None
    email: EmailStr | None = None
    cellphone: str | None = None
    single_session: bool = True
    is_active: bool | None = None
    is_admin: bool | None = None
    mfa_enabled: bool | None = None


class UserSearchRequest(BaseSchema):
    keyword: str | None = None
    size: int = 10
    page: int = 1
