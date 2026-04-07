from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..models.enums import UserRole


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=255, examples=["User Userson"])]
    email: Annotated[str, Field(examples=["user.userson@example.com"])]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    role: UserRole


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    hashed_password: str
    role: UserRole = UserRole.MANAGER


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=255, examples=["User Userberg"], default=None)]
    email: Annotated[str | None, Field(examples=["user.userberg@example.com"], default=None)]


class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
