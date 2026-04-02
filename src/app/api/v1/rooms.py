from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_floor import crud_floors
from ...crud.crud_room import crud_rooms
from ...schemas.floor import FloorRead
from ...schemas.room import RoomCreate, RoomCreateInternal, RoomRead, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"], dependencies=[Depends(get_current_staff)])


@router.post("", response_model=RoomRead, status_code=201)
async def create_room(
    request: Request,
    body: RoomCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    floor = await crud_floors.get(db=db, id=body.floor_id, deleted_at=None, schema_to_select=FloorRead)
    if floor is None:
        raise NotFoundException("Floor not found")

    created = await crud_rooms.create(
        db=db,
        object=RoomCreateInternal.model_validate(body.model_dump()),
        schema_to_select=RoomRead,
    )
    if created is None:
        raise NotFoundException("Failed to create room")
    return created


@router.get("", response_model=list[RoomRead])
async def list_rooms(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    floor_id: Annotated[UUID | None, Query(description="Filter by floor")] = None,
) -> list[Any]:
    kwargs: dict[str, Any] = {
        "limit": None,
        "deleted_at": None,
        "return_total_count": False,
    }
    if floor_id is not None:
        kwargs["floor_id"] = floor_id

    result = await crud_rooms.get_multi(db=db, **kwargs)
    return result["data"]


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(
    request: Request,
    room_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_rooms.get(db=db, id=room_id, deleted_at=None, schema_to_select=RoomRead)
    if row is None:
        raise NotFoundException("Room not found")
    return row


@router.patch("/{room_id}")
async def update_room(
    request: Request,
    room_id: UUID,
    values: RoomUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_rooms.exists(db=db, id=room_id, deleted_at=None):
        raise NotFoundException("Room not found")

    payload = values.model_dump(exclude_unset=True)
    nullable = {"description"}
    payload = {k: v for k, v in payload.items() if v is not None or k in nullable}
    if not payload:
        return {"message": "Nothing to update"}

    if "floor_id" in payload:
        floor = await crud_floors.get(
            db=db, id=payload["floor_id"], deleted_at=None, schema_to_select=FloorRead
        )
        if floor is None:
            raise NotFoundException("Floor not found")

    payload["updated_at"] = datetime.now(UTC)
    await crud_rooms.update(db=db, object=payload, id=room_id)
    return {"message": "Room updated"}


@router.delete("/{room_id}")
async def delete_room(
    request: Request,
    room_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_rooms.exists(db=db, id=room_id, deleted_at=None):
        raise NotFoundException("Room not found")

    await crud_rooms.delete(db=db, id=room_id)
    return {"message": "Room deleted"}
