from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, HTTPException, Query, Request, Security, status, WebSocket
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models import User, UserSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer(auto_error=False)


def get_mfa_user(
    bearer: HTTPAuthorizationCredentials = Security(bearer_scheme),
    oauth2: str | None = Depends(oauth2_scheme),
) -> User:
    token = bearer.credentials if bearer else oauth2
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("token_role") != "mfa":
        raise credentials_exception

    try:
        user_id = UUID(payload.get("id"))
    except Exception as e:
        raise credentials_exception from e

    with get_db() as db:
        user = db.scalar(select(User).options(joinedload(User.profile)).where(User.id == user_id))

    if not user:
        raise credentials_exception

    return user


def get_auth_user(
    bearer: HTTPAuthorizationCredentials = Security(bearer_scheme),
    oauth2: str | None = Depends(oauth2_scheme),
) -> User:
    token = bearer.credentials if bearer else oauth2
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("token_role") == "mfa":
        raise credentials_exception

    try:
        user_id = UUID(payload.get("id"))
        session_id = UUID(payload.get("session_id"))
    except Exception as e:
        raise credentials_exception from e

    query = (
        select(User, UserSession)
        .options(joinedload(User.profile))
        .join(UserSession, UserSession.user_id == User.id)
        .where(User.id == user_id, UserSession.id == session_id)
    )

    with get_db() as db:
        result = db.execute(query).first()

    if not result:
        raise credentials_exception

    user, user_session = result

    now_utc = datetime.now(UTC)

    expire_at = user_session.expire_at
    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=UTC)

    revoked_at = user_session.revoked_at
    if revoked_at is not None and revoked_at.tzinfo is None:
        revoked_at = revoked_at.replace(tzinfo=UTC)

    if revoked_at is not None or expire_at < now_utc:
        raise credentials_exception

    return user


def auth_guard(
    request: Request,
    user: User = Depends(get_auth_user),
) -> None:
    endpoint = request.scope.get("endpoint")

    if endpoint is None:
        return

    roles = getattr(endpoint, "__required_roles__", [])
    profiles = getattr(endpoint, "__required_profiles__", [])

    if user.role == "admin":
        return

    if roles and user.role not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")

    if profiles:
        profile_id = getattr(getattr(user, "profile", None), "id", None)
        if profile_id not in profiles:
            raise HTTPException(status_code=403, detail="Forbidden")


def get_auth_user_ws(
    websocket: WebSocket,
    token: str | None = Query(None),
) -> User:
    if not token:
        # Tenta pegar do header se o cliente suportar
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    try:
        user_id = UUID(payload.get("id"))
        session_id = UUID(payload.get("session_id"))
    except Exception as e:
        raise credentials_exception from e

    query = (
        select(User, UserSession)
        .options(joinedload(User.profile))
        .join(UserSession, UserSession.user_id == User.id)
        .where(User.id == user_id, UserSession.id == session_id)
    )

    with get_db() as db:
        result = db.execute(query).first()

    if not result:
        raise credentials_exception

    user, user_session = result
    now_utc = datetime.now(UTC)
    expire_at = user_session.expire_at
    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=UTC)

    revoked_at = user_session.revoked_at
    if revoked_at is not None and revoked_at.tzinfo is None:
        revoked_at = revoked_at.replace(tzinfo=UTC)

    if revoked_at is not None or expire_at < now_utc:
        raise credentials_exception

    return user
