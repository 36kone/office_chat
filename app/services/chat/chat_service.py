from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.exception_utils import ensure_or_404
from app.models import Chat, ChatUser
from app.schemas import CreateChat, UpdateChat


class ChatService:
    def __init__(self, session: DBSession):
        self.session = session

    def create(self, data: CreateChat) -> Chat:
        # Se for 1:1 e já existir um chat entre esses dois usuários, retornar o existente
        if not data.is_group and len(data.user_ids) == 2:
            # Lógica simples para encontrar chat 1:1 existente
            # (Pode ser melhorada futuramente, mas para MVP vamos criar um novo se não achar fácil)
            pass

        chat = Chat(
            name=data.name,
            is_group=data.is_group
        )
        self.session.add(chat)
        self.session.flush() # Para pegar o ID do chat

        # Adicionar usuários ao chat
        for user_id in data.user_ids:
            chat_user = ChatUser(chat_id=chat.id, user_id=user_id)
            self.session.add(chat_user)

        self.session.commit()
        return self.get_by_id(chat.id)

    def get_by_id(self, id: UUID) -> Chat:
        return ensure_or_404(
            self.session.scalar(select(Chat).where(Chat.id == id, Chat.deleted_at.is_(None))),
            "Chat not found"
        )

    def search(self, user_id: UUID, keyword: str | None = None, size: int = 10, page: int = 1):
        # Listar chats do usuário
        query = (
            self.session.query(Chat)
            .join(ChatUser)
            .filter(ChatUser.user_id == user_id, Chat.deleted_at.is_(None))
        )

        if keyword:
            query = query.filter(Chat.name.ilike(f"%{keyword}%"))

        total = query.count()
        chats = query.offset((page - 1) * size).limit(size).all()
        return chats, total

    def update(self, data: UpdateChat) -> Chat:
        chat = self.get_by_id(data.id)
        if data.name is not None:
            chat.name = data.name
        if data.is_group is not None:
            chat.is_group = data.is_group

        self.session.commit()
        return chat

    def delete(self, id: UUID) -> None:
        chat = self.get_by_id(id)
        chat.deleted_at = func.now()
        self.session.commit()


