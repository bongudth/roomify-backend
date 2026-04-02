from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FloorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class FloorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class FloorCreateInternal(FloorCreate):
    pass


class FloorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class FloorUpdateInternal(FloorUpdate):
    updated_at: datetime


class FloorDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
