from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...core.utils.room_occupancy import (
    compute_room_occupancy_status,
    load_contracts_by_room_ids,
)
from ...crud.crud_floor import crud_floors
from ...crud.crud_room import crud_rooms
from ...models.enums import RoomOccupancyStatus
from ...models.floor import Floor
from ...models.room_type import RoomType
from ...schemas.floor import FloorRead
from ...schemas.room import RoomCreate, RoomCreateInternal, RoomRead, RoomReadRow, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"], dependencies=[Depends(get_current_staff)])


async def _monthly_rents_for_room_types(db: AsyncSession, room_type_ids: Iterable[UUID]) -> dict[UUID, Decimal]:
    ids = list(set(room_type_ids))
    if not ids:
        return {}
    result = await db.execute(select(RoomType.id, RoomType.monthly_rent).where(RoomType.id.in_(ids)))
    return dict(result.all())


def _room_read_from_row(
    row: dict[str, Any],
    monthly_rent: Decimal,
    occupancy_status: RoomOccupancyStatus,
) -> RoomRead:
    return RoomRead(**{**row, "monthly_rent": monthly_rent, "occupancy_status": occupancy_status})


@router.post("", response_model=RoomRead, status_code=201)
async def create_room(
    request: Request,
    body: RoomCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    floor = await crud_floors.get(db=db, id=body.floor_id, deleted_at__is=None, schema_to_select=FloorRead)
    if floor is None:
        raise NotFoundException("Floor not found")

    room_type = await db.get(RoomType, body.room_type_id)
    if room_type is None:
        raise NotFoundException("Room type not found")

    created = await crud_rooms.create(
        db=db,
        object=RoomCreateInternal.model_validate(body.model_dump()),
        schema_to_select=RoomReadRow,
    )
    if created is None:
        raise NotFoundException("Failed to create room")
    today = datetime.now(UTC).date()
    contracts_by_room = await load_contracts_by_room_ids(db, [created["id"]])
    occupancy_status = compute_room_occupancy_status(today, contracts_by_room.get(created["id"], []))
    return _room_read_from_row(created, room_type.monthly_rent, occupancy_status)


@router.get("", response_model=list[RoomRead])
async def list_rooms(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    floor_id: Annotated[UUID | None, Query(description="Filter by floor")] = None,
) -> list[Any]:
    room_filters: dict[str, Any] = {"deleted_at__is": None}
    if floor_id is not None:
        room_filters["floor_id"] = floor_id

    result = await crud_rooms.get_multi_joined(
        db=db,
        schema_to_select=RoomReadRow,
        join_model=Floor,
        join_type="inner",
        join_filters={"deleted_at__is": None},
        offset=0,
        limit=None,
        return_total_count=False,
        **room_filters,
    )
    rows = result["data"]
    today = datetime.now(UTC).date()
    contracts_by_room = await load_contracts_by_room_ids(db, [r["id"] for r in rows])
    rent_by_type = await _monthly_rents_for_room_types(db, (r["room_type_id"] for r in rows))
    return [
        _room_read_from_row(
            r,
            rent_by_type[r["room_type_id"]],
            compute_room_occupancy_status(today, contracts_by_room.get(r["id"], [])),
        )
        for r in rows
    ]


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(
    request: Request,
    room_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_rooms.get(db=db, id=room_id, deleted_at__is=None, schema_to_select=RoomReadRow)
    if row is None:
        raise NotFoundException("Room not found")
    if (
        await crud_floors.get(db=db, id=row["floor_id"], deleted_at__is=None, schema_to_select=FloorRead)
        is None
    ):
        raise NotFoundException("Room not found")
    today = datetime.now(UTC).date()
    contracts_by_room = await load_contracts_by_room_ids(db, [room_id])
    occupancy_status = compute_room_occupancy_status(today, contracts_by_room.get(room_id, []))
    rent_by_type = await _monthly_rents_for_room_types(db, [row["room_type_id"]])
    return _room_read_from_row(row, rent_by_type[row["room_type_id"]], occupancy_status)


@router.patch("/{room_id}")
async def update_room(
    request: Request,
    room_id: UUID,
    values: RoomUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_rooms.exists(db=db, id=room_id, deleted_at__is=None):
        raise NotFoundException("Room not found")

    payload = values.model_dump(exclude_unset=True)
    nullable = {"description"}
    payload = {k: v for k, v in payload.items() if v is not None or k in nullable}
    if not payload:
        return {"message": "Nothing to update"}

    if "floor_id" in payload:
        floor = await crud_floors.get(
            db=db, id=payload["floor_id"], deleted_at__is=None, schema_to_select=FloorRead
        )
        if floor is None:
            raise NotFoundException("Floor not found")

    if "room_type_id" in payload:
        room_type = await db.get(RoomType, payload["room_type_id"])
        if room_type is None:
            raise NotFoundException("Room type not found")

    payload["updated_at"] = datetime.now(UTC)
    await crud_rooms.update(db=db, object=payload, id=room_id)
    return {"message": "Room updated"}


@router.delete("/{room_id}")
async def delete_room(
    request: Request,
    room_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_rooms.exists(db=db, id=room_id, deleted_at__is=None):
        raise NotFoundException("Room not found")

    await crud_rooms.delete(db=db, id=room_id)
    return {"message": "Room deleted"}
