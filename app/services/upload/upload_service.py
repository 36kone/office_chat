import uuid
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exception_utils import ensure_400
from app.schemas.message.message_schema import UploadMessage


class UploadService:
    def __init__(self, session: Session):
        self._session = session

    async def upload(
        self,
        id_: str,
        type_: str,
        file: UploadFile,
        bucket: BucketService,
        current_user: User,
        item_id: str | None = None,
        checklist_id: str | None = None,
    ) -> UploadMessage:
        folder_name = str(uuid.uuid4())

        allowed_types = [
            "video/mp4",
            "image/png",
            "image/jpeg",
            "application/pdf",
        ]

        ensure_400(
            file.content_type not in allowed_types,
            "Invalid file format. Only MP4, PNG, JPEG or PDF are allowed.",
        )

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        ensure_400(file_size > (500 * 1024 * 1024), "File too large, maximum of 500MB.")

        match type_:
            # EXAMPLE OF USAGE

            case "services":
                # entity = self._services_service.get_by_id(UUID(id_))
                # folder_name = entity.name

                ...

            case _:
                ensure_400(True, "Invalid type parameter.")

        extension: str = file.filename.split(".")[-1]
        filename: str = f"{uuid.uuid4()}.{extension}"
        file_path: str = f"{type_}/{folder_name}/{filename}"

        try:
            bucket.upload(
                file_obj=file.file,
                filename=file_path,
                content_type=file.content_type,
                public=False,
            )
        except Exception as e:
            ensure_400(True, f"Failed to upload: {e!s}")

        updated_data = None

        match type_:
            # EXAMPLE OF USAGE

            case "services":
                # entity = self._services_service.get_by_id(UUID(id_))

                # if entity.thumb is not None:
                #    bucket.delete(filename=entity.thumb)

                # updated_data = self._services_service.update(
                #    data=ServiceUpdate(id=UUID(id_), thumb=file_path)
                # )

               ...

            case _:
                ensure_400(True, "Unsupported type for update.")

        ensure_400(not updated_data, "Error updating data.")

        return UploadMessage(
            message="Upload successful!",
            path=f"{bucket.get_presigned_url(file_path)}",
        )

    def delete(self, id_: UUID, type_: str, bucket: BucketService) -> dict:
        match type_:
            # EXAMPLE OF USAGE

            case "services":
                # entity = self._services_service.get_by_id(id_)
                # bucket.delete(filename=entity.path)
                # entity.path = None
                # self._session.commit()

                ...

            case _:
                ensure_400(True, "Unsupported type for delete.")

        return {"message": "File deleted successfully."}
