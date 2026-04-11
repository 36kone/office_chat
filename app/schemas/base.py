from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

SP_TZ = ZoneInfo("America/Sao_Paulo")
UTC = UTC


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    __allow_empty_strings__ = {"keyword"}

    @model_validator(mode="before")
    @classmethod
    def validate_empty_strings(cls, values: Any):
        if isinstance(values, dict):
            for field, value in values.items():
                if field in cls.__allow_empty_strings__:
                    continue

                if isinstance(value, str) and value.strip() == "":
                    raise ValueError(f"The field '{field}' cannot be an empty string.")

        return values


# CONVERTE O TIMESTAMP DO DB DE UTC PARA FUSO DE SP
class TimestampedResponse:
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    @field_validator(
        "created_at",
        "updated_at",
        "deleted_at",
        mode="before",
    )
    @classmethod
    def convert_utc_to_sp(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value

        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)

        return value.astimezone(SP_TZ)
