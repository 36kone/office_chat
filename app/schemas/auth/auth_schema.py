from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.base import BaseSchema


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    new_password: str
    token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class Enable2FARequest(BaseModel):
    code: str


class UserFirstAccessResponse(BaseModel):
    id: UUID
    name: str
    username: str
    email: EmailStr
    birthdate: date


class VerifyUserByPassword(BaseSchema):
    password: str
