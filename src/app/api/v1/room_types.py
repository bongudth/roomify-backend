from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ...crud.crud_room import crud_rooms
from ...crud.crud_room_type import crud_room_types
from ...schemas.room_type import RoomTypeCreate, RoomTypeCreateInternal, RoomTypeRead, RoomTypeUpdate

ROOM_TYPE_NOT_FOUND = "Room type not found"

router = APIRouter(prefix="/room-types", tags=["room-types"], dependencies=[Depends(get_current_staff)])


@router.post("", response_model=RoomTypeRead, status_code=201)
async def create_room_type(
    request: Request,
    body: RoomTypeCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    created = await crud_room_types.create(
        db=db,
        object=RoomTypeCreateInternal.model_validate(body.model_dump()),
        schema_to_select=RoomTypeRead,
    )
    if created is None:
        raise NotFoundException("Failed to create room type")
    return created


@router.get("", response_model=list[RoomTypeRead])
async def list_room_types(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[Any]:
    result = await crud_room_types.get_multi(
        db=db,
        limit=None,
        schema_to_select=RoomTypeRead,
        return_total_count=False,
    )
    return result["data"]


@router.get("/{room_type_id}", response_model=RoomTypeRead)
async def get_room_type(
    request: Request,
    room_type_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_room_types.get(db=db, id=room_type_id, schema_to_select=RoomTypeRead)
    if row is None:
        raise NotFoundException(ROOM_TYPE_NOT_FOUND)
    return row


@router.patch("/{room_type_id}")
async def update_room_type(
    request: Request,
    room_type_id: UUID,
    values: RoomTypeUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    existing = await crud_room_types.get(db=db, id=room_type_id, schema_to_select=RoomTypeRead)
    if existing is None:
        raise NotFoundException(ROOM_TYPE_NOT_FOUND)

    payload = values.model_dump(exclude_unset=True)
    nullable = {"description"}
    payload = {k: v for k, v in payload.items() if v is not None or k in nullable}
    if not payload:
        return {"message": "Nothing to update"}

    await crud_room_types.update(db=db, object=payload, id=room_type_id)
    return {"message": "Room type updated"}


@router.delete("/{room_type_id}")
async def delete_room_type(
    request: Request,
    room_type_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_room_types.exists(db=db, id=room_type_id):
        raise NotFoundException(ROOM_TYPE_NOT_FOUND)

    if await crud_rooms.exists(db=db, room_type_id=room_type_id):
        raise BadRequestException("Cannot delete a room type that is still assigned to one or more rooms.")

    await crud_room_types.delete(db=db, id=room_type_id)
    return {"message": "Room type deleted"}
