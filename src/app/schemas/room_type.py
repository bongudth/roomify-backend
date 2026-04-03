from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoomTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    monthly_rent: Decimal
    description: str | None
    created_at: datetime


class RoomTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=255)]
    monthly_rent: Annotated[Decimal, Field(ge=Decimal("0"), max_digits=14, decimal_places=2)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomTypeCreateInternal(RoomTypeCreate):
    pass


class RoomTypeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)]
    monthly_rent: Annotated[Decimal | None, Field(default=None, ge=Decimal("0"), max_digits=14, decimal_places=2)]
    description: Annotated[str | None, Field(default=None, max_length=10_000)]


class RoomTypeUpdateInternal(RoomTypeUpdate):
    pass


class RoomTypeDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
