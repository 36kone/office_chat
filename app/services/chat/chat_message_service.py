from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.exception_utils import ensure_400
from app.models import ChatMessage, ChatUser
from app.schemas import CreateChatMessage


class MessageService:
    def __init__(self, session: DBSession):
        self.session = session

    def send_message(self, sender_id: UUID, data: CreateChatMessage) -> ChatMessage:
        # Validar se o usuário pertence ao chat
        is_member = self.session.scalar(
            select(ChatUser).where(
                ChatUser.chat_id == data.chat_id,
                ChatUser.user_id == sender_id
            )
        )
        ensure_400(not is_member, "User is not a member of this chat")

        message = ChatMessage(
            chat_id=data.chat_id,
            sender_id=sender_id,
            content=data.content
        )
        self.session.add(message)
        self.session.commit()
        return message

    def get_chat_history(self, chat_id: UUID, size: int = 50, page: int = 1):
        query = (
            self.session.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id, ChatMessage.deleted_at.is_(None))
            .order_by(ChatMessage.created_at.desc())
        )

        total = query.count()
        messages = query.offset((page - 1) * size).limit(size).all()
        # Inverter para vir na ordem cronológica
        return messages[::-1], total
