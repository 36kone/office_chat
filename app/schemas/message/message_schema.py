from datetime import datetime

from ..base import BaseSchema


class Message(BaseSchema):
    message: str


class UploadMessage(BaseSchema):
    message: str
    path: str


class HealthMessageResponse(BaseSchema):
    client_ip: str
    server_ip: str
    current_date_time: datetime
    api_version: str
    message: str
