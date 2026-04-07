from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    phone: str
    id_number: str
    address: str | None
    birthday: date | None
    email: str | None
    created_at: datetime
    updated_at: datetime


class TenantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Annotated[str, Field(min_length=1, max_length=255)]
    phone: Annotated[str, Field(min_length=1, max_length=32)]
    id_number: Annotated[str, Field(min_length=1, max_length=64)]
    address: Annotated[str | None, Field(default=None, max_length=10_000)]
    birthday: date | None = None
    email: str | None = None


class TenantCreateInternal(TenantCreate):
    pass


class TenantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)]
    phone: Annotated[str | None, Field(default=None, min_length=1, max_length=32)]
    id_number: Annotated[str | None, Field(default=None, min_length=1, max_length=64)]
    address: Annotated[str | None, Field(default=None, max_length=10_000)]
    birthday: date | None = None
    email: str | None = None


class TenantUpdateInternal(TenantUpdate):
    updated_at: datetime


class TenantDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
