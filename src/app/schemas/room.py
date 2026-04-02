from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    floor_id: UUID
    capacity: int
    monthly_rent: Decimal
    description: str | None
    created_at: datetime
    updated_at: datetime


class RoomCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=255)]
    floor_id: UUID
    capacity: Annotated[int, Field(ge=1, le=500)]
    monthly_rent: Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)]
    floor_id: Annotated[UUID | None, Field(default=None)]
    capacity: Annotated[int | None, Field(default=None, ge=1, le=500)]
    monthly_rent: Annotated[Decimal | None, Field(default=None, gt=0, max_digits=14, decimal_places=2)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomUpdateInternal(RoomUpdate):
    updated_at: datetime


class RoomDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
