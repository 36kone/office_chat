from fastapi import APIRouter

from .auth.auth_routes import auth_router
from .chat.chat_routes import chat_router, ws_router
from .upload.upload_routes import upload_router
from .user.user_routes import user_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(user_router, prefix="/users", tags=["Users"])

api_router.include_router(
    chat_router,
    prefix="/chats",
    tags=["Chats"],
)

api_router.include_router(
    ws_router,
    prefix="/chats",
    tags=["Chats"],
)

api_router.include_router(
    upload_router,
    prefix="/upload",
    tags=["Upload"],
)
