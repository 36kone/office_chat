import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.dependencies.authentication import auth_guard, get_auth_user
from app.models import User
from app.schemas import (
    ChatResponse,
    ChatSearchRequest,
    CreateChat,
    PaginatedResponse,
    UpdateChat,
)
from app.services import ChatService

chat_router = APIRouter(dependencies=[Depends(auth_guard)])
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
