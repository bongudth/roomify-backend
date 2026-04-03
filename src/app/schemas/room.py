from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..models.enums import RoomOccupancyStatus


class RoomReadRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    floor_id: UUID
    room_type_id: UUID
    capacity: int
    description: str | None
    created_at: datetime
    updated_at: datetime


class RoomRead(RoomReadRow):
    monthly_rent: Decimal
    occupancy_status: RoomOccupancyStatus


class RoomCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=255)]
    floor_id: UUID
    room_type_id: UUID
    capacity: Annotated[int, Field(ge=1, le=500)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomCreateInternal(RoomCreate):
    pass


class RoomUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)]
    floor_id: Annotated[UUID | None, Field(default=None)]
    room_type_id: Annotated[UUID | None, Field(default=None)]
    capacity: Annotated[int | None, Field(default=None, ge=1, le=500)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomUpdateInternal(RoomUpdate):
    updated_at: datetime


class RoomDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
