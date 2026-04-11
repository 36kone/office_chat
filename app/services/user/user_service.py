from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session as DBSession

from app.core.exception_utils import (
    ensure_400,
    ensure_or_400,
    ensure_or_404,
)
from app.core.security import get_password_hash, verify_password
from app.models import User, UserSession
from app.schemas import (
    CreateUser,
    UpdateUser,
)


class UserService:
    def __init__(self, session: DBSession):
        self.session = session

    def _validate_user_creation(self, data: CreateUser) -> None:
        conditions = []

        if data.email:
            conditions.append(User.email == data.email)

        if conditions:
            duplicate = self.session.scalar(
                select(User.id).where(User.deleted_at.is_(None), or_(*conditions))
            )
            ensure_400(duplicate, "User already registered")

    def _validate_user_update_data(self, data: UpdateUser) -> None:
        conditions = []

        if data.email:
            conditions.append(User.email == data.email)

        if conditions:
            duplicate = self.session.scalar(
                select(User.id).where(
                    User.deleted_at.is_(None), User.id != data.id, or_(*conditions)
                )
            )
            ensure_400(duplicate, "Already exists a user with this datas.")

    def _validate_single_session(self, user_id: UUID) -> None:
        user = self.session.scalar(select(User).where(User.id == user_id))

        if user.single_session:
            self.session.execute(
                update(UserSession)
                .where(and_(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)))
                .values(revoked_at=datetime.now(UTC))
            )
            self.session.commit()

    def create(self, data: CreateUser) -> User:
        self._validate_user_creation(data)

        entity = User(
            name=data.name,
            email=str(data.email),
            password=get_password_hash(data.password),
            cellphone=data.cellphone,
            is_admin=data.is_admin,
            single_session=data.single_session,
        )

        self.session.add(entity)
        self.session.commit()
        return self.get_by_id(entity.id)

    async def search(self, keyword: str, size: int, page: int):
        query = (
            self.session.query(User)
            .filter(User.deleted_at.is_(None))
            .order_by(User.name.asc())
        )

        if keyword:
            query = query.filter(
                or_(User.name.ilike(f"%{keyword}%"), User.email.ilike(f"%{keyword}%"))
            )

        total = query.count()
        users = query.offset((page - 1) * size).limit(size).all()
        return users, total

    def get_by_id(self, id_: UUID) -> User:
        return ensure_or_404(
            self.session.scalar(
                select(User)
                .where(
                    User.id == id_,
                    User.deleted_at.is_(None),
                )
            ),
            "User not found",
        )

    def get_by_email(self, email: EmailStr) -> User:
        return self.session.scalar(
            select(User)
            .where(
                User.email == email,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )

    def get_by_username(self, username: str) -> User:
        return self.session.scalar(
            select(User)
            .where(
                User.username == username,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )

    async def get_by_password_reset_token(self, token: str) -> User:
        return ensure_or_404(
            self.session.scalar(
                select(User)
                .where(
                    User.password_recovery == token,
                    User.password_recovery_expire >= datetime.now(UTC),
                )
            ),
            "Not a valid token or expired",
        )

    def verify_by_password(self, password: str, id_: UUID) -> bool:
        user = self.get_by_id(id_)

        ensure_400(user is None, "Incorrect email or password.")
        ensure_or_400(
            verify_password(password, user.password),
            "Invalid credentials.",
        )
        return True

    def update(self, data: UpdateUser) -> User:
        entity = self.get_by_id(data.id)

        self._validate_user_update_data(entity)

        if data.mfa_enabled is False:
            entity.mfa_enabled = False
            entity.mfa_secret = None

        try:
            data_dict = data.model_dump(exclude_unset=True)

            for field, value in data_dict.items():
                setattr(entity, field, value)

            self.session.commit()
            return self.get_by_id(entity.id)

        except Exception as error:
            self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Update failed - {error}") from error

    async def update_password(self, user: User, new_password: str) -> None:
        try:
            user.password = get_password_hash(new_password)
            user.password_recovery = datetime.now(UTC)
            user.password_recovery_expire = None

            self.session.commit()

        except Exception as error:
            self.session.rollback()
            ensure_400(True, f"Password update failed: {error}")

    async def update_user_password_reset_token(self, email: EmailStr, token: str) -> None:
        entity = ensure_or_404(self.get_by_email(email))

        entity.password_recovery = token
        entity.password_recovery_expire = datetime.now(UTC) + timedelta(hours=1)

        self.session.commit()

    def delete(self, id_: UUID) -> None:
        entity = self.get_by_id(id_)

        if entity.deleted_at is not None:
            raise HTTPException(404, "Not found")

        entity.deleted_at = datetime.now(UTC)
        self.session.commit()
