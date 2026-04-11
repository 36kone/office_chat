import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.db.database import get_db
from app.dependencies.authentication import auth_guard, get_auth_user, get_auth_user_ws
from app.models import ChatUser, User
from app.schemas import (
    ChatMessageResponse,
    ChatResponse,
    ChatSearchRequest,
    CreateChat,
    CreateChatMessage,
    PaginatedResponse,
    UpdateChat,
)
from app.services import ChatService, MessageService, manager

chat_router = APIRouter(dependencies=[Depends(auth_guard)])
ws_router = APIRouter() # Router sem o auth_guard global
logger = logging.getLogger("chats")


@chat_router.post("/", status_code=201, response_model=ChatResponse)
def create_chat(data: CreateChat):
    try:
        with get_db() as db:
            service = ChatService(db)
            return service.create(data)
    except HTTPException as exc:
        logger.error(f"[CREATE_CHAT] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[CREATE_CHAT] -> {e}")
        raise e


@chat_router.post("/search", status_code=200, response_model=PaginatedResponse[ChatResponse])
def search_chats_endpoint(
    search_request: ChatSearchRequest,
    current_user: User = Depends(get_auth_user)
):
    try:
        with get_db() as db:
            service = ChatService(db)

            chats, total = service.search(
                user_id=current_user.id,
                keyword=search_request.keyword,
                size=search_request.size,
                page=search_request.page,
            )

            return PaginatedResponse.create(
                total=total,
                page=search_request.page,
                size=search_request.size,
                items=[ChatResponse.model_validate(c, from_attributes=True) for c in chats],
            )
    except HTTPException as exc:
        logger.error(f"[SEARCH_CHATS] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[SEARCH_CHATS] -> {e}")
        raise e


@chat_router.get("/{id_}", status_code=200, response_model=ChatResponse)
def get_chat_by_id(id_: UUID):
    try:
        with get_db() as db:
            service = ChatService(db)
            return service.get_by_id(id_)
    except HTTPException as exc:
        logger.error(f"[GET_CHAT_BY_ID] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[GET_CHAT_BY_ID] -> {e}")
        raise e


@chat_router.put("/{id_}", status_code=200, response_model=ChatResponse)
def update_chat(data: UpdateChat):
    try:
        with get_db() as db:
            service = ChatService(db)
            return service.update(data)
    except HTTPException as exc:
        logger.error(f"[UPDATE_CHAT] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[UPDATE_CHAT] -> {e}")
        raise e


@chat_router.delete("/{id_}", status_code=204)
def delete_chat(id_: UUID):
    try:
        with get_db() as db:
            service = ChatService(db)
            service.delete(id_)
    except HTTPException as exc:
        logger.error(f"[DELETE_CHAT] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[DELETE_CHAT] -> {e}")
        raise e


@chat_router.get("/{id_}/history", response_model=PaginatedResponse[ChatMessageResponse])
def get_chat_history(id_: UUID, size: int = 50, page: int = 1):
    try:
        with get_db() as db:
            service = MessageService(db)
            messages, total = service.get_chat_history(id_, size, page)

            return PaginatedResponse.create(
                total=total,
                page=page,
                size=size,
                items=[ChatMessageResponse.model_validate(m, from_attributes=True) for m in messages],
            )
    except HTTPException as exc:
        logger.error(f"[GET_CHAT_HISTORY] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[GET_CHAT_HISTORY] -> {e}")
        raise e


@ws_router.websocket("/ws")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(get_auth_user_ws)
):
    await manager.connect(user.id, websocket)
    try:
        while True:
            # Recebe dados do cliente
            data = await websocket.receive_json()

            # Processa a mensagem
            with get_db() as db:
                message_service = MessageService(db)

                # Assume que o front envia algo compatível com CreateChatMessage
                # Ex: {"chat_id": "...", "content": "..."}
                try:
                    create_data = CreateChatMessage(**data)
                    new_message = message_service.send_message(user.id, create_data)

                    # Busca todos os usuários desse chat para fazer o broadcast
                    chat_users = db.query(ChatUser.user_id).filter(ChatUser.chat_id == create_data.chat_id).all()
                    user_ids = [cu.user_id for cu in chat_users]

                    # Prepara a resposta (serializada)
                    response_data = ChatMessageResponse.model_validate(new_message, from_attributes=True).model_dump(mode='json')

                    # Envia para todos os membros do chat que estão online
                    await manager.broadcast_to_users(response_data, user_ids)

                except Exception as e:
                    logger.error(f"[WS_MESSAGE_ERROR] -> {e}")
                    await manager.send_personal_message({"error": str(e)}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
    except Exception as e:
        logger.error(f"[WS_ERROR] -> {e}")
        manager.disconnect(user.id, websocket)
