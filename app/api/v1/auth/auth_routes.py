import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import get_db
from app.dependencies.authentication import get_auth_user, get_mfa_user, oauth2_scheme
from app.dependencies.current_user import CurrentUser
from app.dependencies.rate_limit_route import rate_limited
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    Enable2FARequest,
    Message,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserResponse,
    VerifyUserByPassword,
)
from app.services import AuthService, UserService

auth_router = APIRouter(route_class=rate_limited(default_limit="100/minute"))
logger = logging.getLogger("auth")


@auth_router.post("/login", response_model=Token | dict)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.login(request, form_data)
    except HTTPException as exc:
        logger.error(f"[LOGIN] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[LOGIN] -> {e}")
        raise e


@auth_router.post("/verify-by-password")
def verify_user_by_password(current_user: CurrentUser, data: VerifyUserByPassword):
    try:
        with get_db() as db:
            service = UserService(db)

            return service.verify_by_password(data.password, current_user.id)
    except HTTPException as exc:
        logger.error(f"[VERIFY USER BY PASSWORD] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[VERIFY USER BY PASSWORD] -> {e}")
        raise e


@auth_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_auth_user)):
    try:
        return current_user
    except HTTPException as exc:
        logger.error(f"[GET ME] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[GET ME] -> {e}")
        raise e


@auth_router.post("/forgot-password", status_code=200, response_model=Message)
async def request_password_reset(data: PasswordResetRequest):
    try:
        with get_db() as db:
            service = AuthService(db)

            return await service.request_password_reset(data)
    except HTTPException as exc:
        logger.error(f"[REQUEST_PASSWORD_RESET] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[REQUEST_PASSWORD_RESET] -> {e}")
        raise e


@auth_router.put("/change-password", status_code=200, response_model=Message)
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_auth_user)):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.change_password(data, current_user.id)
    except HTTPException as exc:
        logger.error(f"[CHANGE_PASSWORD] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[CHANGE_PASSWORD] -> {e}")
        raise e


@auth_router.post("/reset-password", status_code=200, response_model=Message)
async def confirm_password_reset(data: PasswordResetConfirm):
    try:
        with get_db() as db:
            service = AuthService(db)

            return await service.confirm_password_reset(data)
    except HTTPException as exc:
        logger.error(f"[CONFIRM_PASSWORD_RESET] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[CONFIRM_PASSWORD_RESET] -> {e}")
        raise e


@auth_router.post("/verify-2fa/{code}", status_code=200, response_model=Token)
def verify_2fa(code: str, request: Request, token: str = Depends(oauth2_scheme)):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.verify_2fa(code, request, token)
    except HTTPException as exc:
        logger.error(f"[VERIFY_2FA] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[VERIFY_2FA] -> {e}")
        raise e


@auth_router.post("/setup-2fa", status_code=200)
def setup_2fa(
    current_user: User = Depends(get_auth_user),
):
    try:
        with get_db() as db:
            service = AuthService(db)

            otp_secret, uri = service.setup_2fa(current_user.id)

            return {"otp_secret": otp_secret, "otpauth_url": uri}
    except HTTPException as exc:
        logger.error(f"[SETUP_2FA] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[SETUP_2FA] -> {e}")
        raise e


@auth_router.post("/enable-2fa", status_code=200)
def enable_2fa(payload: Enable2FARequest, current_user: User = Depends(get_mfa_user)):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.enable_2fa(payload, current_user.id)
    except HTTPException as exc:
        logger.error(f"[ENABLE_2FA] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[ENABLE_2FA] -> {e}")
        raise e


@auth_router.post("/me/enable-2fa", status_code=200)
def enable_2fa_for_authenticated_user(
    payload: Enable2FARequest, current_user: User = Depends(get_auth_user)
):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.enable_2fa(payload, current_user.id)
    except HTTPException as exc:
        logger.error(f"[ENABLE_2FA] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[ENABLE_2FA] -> {e}")
        raise e


@auth_router.post("/disable-2fa", status_code=200)
def disable_2fa(
    current_user: User = Depends(get_auth_user),
):
    try:
        with get_db() as db:
            service = AuthService(db)

            return service.disable_2fa(current_user.id)
    except HTTPException as exc:
        logger.error(f"[DISABLE_2FA] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[DISABLE_2FA] -> {e}")
        raise e
