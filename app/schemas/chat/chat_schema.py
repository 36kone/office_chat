from uuid import UUID

from pydantic import ConfigDict

from ..base import BaseSchema, TimestampedResponse
from ..user.user_schema import SimpleUserResponse


# --- CHAT SCHEMAS ---
class CreateChat(BaseSchema):
    name: str | None = None
    is_group: bool = False
    user_ids: list[UUID] = []

class ChatResponse(BaseSchema, TimestampedResponse):
    id: UUID
    name: str | None = None
    is_group: bool

    model_config = ConfigDict(from_attributes=True)

class UpdateChat(BaseSchema):
    id: UUID
    name: str | None = None
    is_group: bool | None = None

class ChatSearchRequest(BaseSchema):
    keyword: str | None = None
    size: int = 10
    page: int = 1

# --- CHAT USER SCHEMAS ---
class CreateChatUser(BaseSchema):
    chat_id: UUID
    user_id: UUID

class ChatUserResponse(BaseSchema):
    id: UUID
    chat_id: UUID
    user_id: UUID
    user: SimpleUserResponse | None = None

    model_config = ConfigDict(from_attributes=True)

# --- CHAT MESSAGE SCHEMAS ---
class CreateChatMessage(BaseSchema):
    chat_id: UUID
    content: str

class ChatMessageResponse(BaseSchema, TimestampedResponse):
    id: UUID
    chat_id: UUID
    sender_id: UUID | None = None
    content: str
    sender: SimpleUserResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class UpdateChatMessage(BaseSchema):
    id: UUID
    content: str
