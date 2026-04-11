from datetime import UTC, datetime, timedelta
import uuid
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exception_utils import ensure_or_404
from app.models import User, UserSession
from app.schemas import UserSessionUpdate


class UserSessionService:
    def __init__(self, session: Session):
        self.session = session

    def create_user_session(
        self,
        user: User,
        user_agent: str | None = None,
    ) -> UserSession:
        if user and user.single_session:
            self.revoke_user_session(user.id)

        user_session = UserSession(
            id=uuid.uuid4(),
            user_id=user.id,
            expire_at=datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE),
            user_agent=user_agent,
        )

        self.session.add(user_session)
        self.session.commit()
        return user_session

    def get_by_id(self, id_: UUID) -> UserSession:
            return ensure_or_404(
            self.session.scalar(select(UserSession).where(UserSession.id == id_)),
            "User session not found",
        )

    def get_by_user_id(self, user_id: UUID) -> UserSession | None:
        return self.session.scalar(
            select(UserSession)
            .order_by(UserSession.created_at.desc())
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
            )
        )

    def update(self, data: UserSessionUpdate) -> UserSession:
        entity = self.get_by_id(data.id)

        try:
            data_dict = data.model_dump(exclude_unset=True)

            for field, value in data_dict.items():
                setattr(entity, field, value)

            self.session.commit()
            return entity

        except HTTPException as error:
            self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Update failed - {error}") from error

    def revoke_user_session(self, user_id: UUID) -> None:
        self.session.execute(
            update(UserSession)
            .where(and_(UserSession.user_id == user_id, UserSession.revoked_at.is_(None)))
            .values(revoked_at=datetime.now(UTC))
        )
        self.session.commit()
