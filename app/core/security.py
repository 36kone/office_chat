from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Query
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas import CreateToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: CreateToken, expires_delta: timedelta | None = None) -> str:
    data = data.model_dump()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_first_access_payload(token: str = Query(...)) -> dict:
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "first_access":
        raise HTTPException(status_code=403, detail="Access denied")
    return payload
