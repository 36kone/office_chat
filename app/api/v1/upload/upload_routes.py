import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.db.database import get_db
from app.dependencies.authentication import auth_guard, required_permissions
from app.dependencies.current_user import CurrentUser
from app.schemas.message.message_schema import Message, UploadMessage
from app.services import BucketService, UploadService, get_bucket_service

upload_router = APIRouter(dependencies=[Depends(auth_guard)])
logger = logging.getLogger("upload")


@upload_router.post("/{id_}/{type_}", status_code=200, response_model=UploadMessage)
@required_permissions()
async def upload_file(
    id_: str,
    type_: str,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    item_id: str | None = Query(default=None),
    checklist_id: str | None = Query(default=None),
    bucket: BucketService = Depends(get_bucket_service),
):
    try:
        with get_db() as db:
            service = UploadService(db)

            return await service.upload(
                id_=id_,
                type_=type_,
                file=file,
                bucket=bucket,
                current_user=current_user,
                item_id=item_id,
                checklist_id=checklist_id,
            )
    except HTTPException as exc:
        logger.error(f"[UPLOAD] -> {exc}")
        raise
    except Exception as e:
        logger.error(f"[UPLOAD] -> {e}")
        raise


@upload_router.delete("/{id_}/{type_}", status_code=200, response_model=Message)
@required_permissions()
async def delete_file(
    id_: UUID,
    type_: str,
    bucket: BucketService = Depends(get_bucket_service),
):
    try:
        with get_db() as db:
            service = UploadService(db)

            return service.delete(id_=id_, type_=type_, bucket=bucket)
    except HTTPException as exc:
        logger.error(f"[DELETE_FILE] -> {exc}")
        raise
    except Exception as e:
        logger.error(f"[DELETE_FILE] -> {e}")
        raise
