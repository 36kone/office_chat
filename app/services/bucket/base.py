from abc import ABC, abstractmethod
from typing import BinaryIO


class BucketService(ABC):
    @abstractmethod
    def upload(
        self, file_obj: BinaryIO, filename: str, content_type: str, public: bool = False
    ) -> str:
        pass

    @abstractmethod
    def delete(self, filename: str) -> None:
        pass

    @abstractmethod
    def get_url(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_presigned_url(self, filename: str, expires_in: int = 3600) -> str:
        pass
