from fastapi import APIRouter

from .upload.upload_routes import upload_router

api_router = APIRouter()

api_router.include_router(
    upload_router,
    prefix="/upload",
    tags=["Upload"],
)
