import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.dependencies.authentication import auth_guard
from app.schemas import (
    CreateUser,
    PaginatedResponse,
    UpdateUser,
    UserResponse,
    UserSearchRequest,
)
from app.services import UserService

user_router = APIRouter(dependencies=[Depends(auth_guard)])
logger = logging.getLogger("users")


@user_router.post("/", status_code=201, response_model=UserResponse)
def create_user(data: CreateUser):
    try:
        with get_db() as db:
            service = UserService(db)

            return service.create(data)
    except HTTPException as exc:
        logger.error(f"[CREATE_USER] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[CREATE_USER] -> {e}")
        raise e


@user_router.post("/search", status_code=200, response_model=PaginatedResponse[UserResponse])
async def search_user_endpoint(search_request: UserSearchRequest):
    try:
        with get_db() as db:
            service = UserService(db)

            users, total = await service.search(
                keyword=search_request.keyword,
                size=search_request.size,
                page=search_request.page,
            )

            return PaginatedResponse.create(
                total=total,
                page=search_request.page,
                size=search_request.size,
                items=[UserResponse.model_validate(u, from_attributes=True) for u in users],
            )
    except HTTPException as exc:
        logger.error(f"[SEARCH_USERS] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[SEARCH_USERS] -> {e}")
        raise e


@user_router.get("/{id_}", status_code=200, response_model=UserResponse)
def get_user_by_id(id_: UUID):
    try:
        with get_db() as db:
            service = UserService(db)

            return service.get_by_id(id_)
    except HTTPException as exc:
        logger.error(f"[GET_USER_BY_ID] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[GET_USER_BY_ID] -> {e}")
        raise e


@user_router.put("/{id_}", status_code=200, response_model=UserResponse)
def update_user(data: UpdateUser):
    try:
        with get_db() as db:
            service = UserService(db)

            return service.update(data)
    except HTTPException as exc:
        logger.error(f"[UPDATE_USER] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[UPDATE_USER] -> {e}")
        raise e


@user_router.delete("/{id_}", status_code=204)
def delete_user(id_: UUID):
    try:
        with get_db() as db:
            service = UserService(db)

            service.delete(id_)
    except HTTPException as exc:
        logger.error(f"[DELETE_USER] -> {exc}")
        raise exc
    except Exception as e:
        logger.error(f"[DELETE_USER] -> {e}")
        raise e
