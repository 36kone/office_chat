from datetime import timedelta
import secrets
from uuid import UUID

from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.v1 import EmailStr
import pyotp
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.exception_utils import (
    ensure_400,
    ensure_or_400,
    ensure_or_404,
)
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.dependencies.email_sender import EmailSender
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    CreateToken,
    Enable2FARequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    SimpleUserResponse,
    Token,
)
from app.services.user.user_service import UserService
from app.services.user.user_session_service import UserSessionService


class AuthService:
    def __init__(self, session: DBSession):
        self.session = session
        self.user_session_service = UserSessionService(self.session)
        self.user_service = UserService(self.session)
        self._email_sender = EmailSender()

    def _create_user_access_token(self, user: User, user_agent: str | None) -> Token:
        user_session = self.user_session_service.create_user_session(
            user, user_agent=user_agent
        )
        access_token = create_access_token(
            data=CreateToken(
                id=str(user.id),
                token_role="admin" if user.is_admin else "user",
                session_id=str(user_session.id),
            )
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=SimpleUserResponse.model_validate(user),
            token_role="admin" if user.is_admin else "user",
        )

    def login(
        self,
        request: Request,
        form_data: OAuth2PasswordRequestForm,
    ) -> Token | dict:
        identifier = EmailStr(form_data.username.strip())
        user = self.user_service.get_by_email(email=identifier)

        ensure_400(user is None, "Incorrect email or password.")

        ensure_or_400(
            verify_password(form_data.password, user.password),
            "Incorrect email or password",
        )

        if user.mfa_enabled and user.mfa_secret is None:
            otp_secret, uri = self.setup_2fa(user_id=user.id)

            temp_token = create_access_token(
                CreateToken(id=str(user.id), token_role="mfa"),
                expires_delta=timedelta(minutes=5),
            )

            return {"access_token": temp_token, "otp_secret": otp_secret, "otpauth_url": uri}

        if user.mfa_enabled and user.mfa_secret is not None:
            temp_token = create_access_token(
                CreateToken(id=str(user.id), token_role="mfa"),
                expires_delta=timedelta(minutes=5),
            )

            return Token(
                access_token=temp_token,
                token_type="bearer",
                user=SimpleUserResponse.model_validate(user),
                token_role="mfa",
            )

        user_agent: str | None = request.headers.get("user-agent")

        return self._create_user_access_token(user=user, user_agent=user_agent)


    def change_password(
        self,
        data: ChangePasswordRequest,
        user_id: UUID,
    ) -> dict:
        current_user = self.user_service.get_by_id(user_id)
        ensure_or_400(
            verify_password(data.current_password, current_user.password),
            "Current password is incorrect",
        )

        current_user.password = get_password_hash(data.new_password)
        self.session.commit()
        self.session.refresh(current_user)

        return {"message": "Password changed successfully"}

    async def request_password_reset(
        self,
        data: PasswordResetRequest,
    ) -> dict:
        user = ensure_or_404(self.user_service.get_by_email(data.email))

        reset_token = secrets.token_urlsafe(32)

        await self.user_service.update_user_password_reset_token(
            email=data.email, token=reset_token
        )

        reset_url = f"{settings.OFFICE_CHAT_URL}/reset-password?token={reset_token}"

        await self._email_sender.send_email(
            subject="Recuperação de Senha",
            email_to=data.email,
            template_path="app/templates/password_reset.html",
            context={"username": user.name, "reset_url": reset_url},
        )
        return {"message": "Email for reset password sent successfully"}

    async def confirm_password_reset(
        self,
        data: PasswordResetConfirm,
    ) -> dict:
        user = ensure_or_400(
            await self.user_service.get_by_password_reset_token(data.token),
            "Token inválido ou expirado",
        )
        await self.user_service.update_password(user, data.new_password)
        return {"message": "Senha redefinida com sucesso"}

    def verify_2fa(
        self,
        code: str,
        request: Request,
        token: str,
    ) -> Token:
        payload = decode_access_token(token)
        if payload.get("token_role") != "mfa":
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_id = payload.get("id")
        user = ensure_or_400(self.user_service.get_by_id(user_id), "User not found")

        ipv4 = request.client.host
        user_agent = request.headers.get("user-agent")

        totp = pyotp.TOTP(user.mfa_secret)
        ensure_or_400(totp.verify(code), "Invalid code")
        return self._create_user_access_token(user, ipv4=ipv4, user_agent=user_agent)

    def setup_2fa(self, user_id: UUID) -> tuple[str, str]:
        current_user = self.user_service.get_by_id(user_id)

        if current_user.mfa_secret and current_user.mfa_secret:
            ensure_400(True, "Two-factor authentication already activated")

        secret = pyotp.random_base32()
        current_user.mfa_secret = secret

        self.session.commit()

        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=current_user.email, issuer_name="OfficeChat"
        )

        return secret, uri

    def enable_2fa(
        self,
        payload: Enable2FARequest,
        user_id: UUID,
    ) -> dict:
        current_user = self.user_service.get_by_id(user_id)

        ensure_or_400(not current_user.mfa_secret, "2FA already activated")

        totp = pyotp.TOTP(current_user.mfa_secret)
        ensure_or_400(totp.verify(payload.code), "Invalid code")

        current_user.mfa_enabled = True

        self.session.commit()
        return {"message": "2fa activated"}

    def disable_2fa(self, user_id: UUID) -> dict:
        current_user = self.user_service.get_by_id(user_id)

        ensure_or_400(current_user.mfa_enabled, "2FA already disabled")

        current_user.mfa_enabled = False
        current_user.mfa_secret = None

        self.session.commit()
        self.session.refresh(current_user)
        return {"message": "2fa disabled"}
