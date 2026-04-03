from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.api_error_codes import (
    API_ERROR_MESSAGES_EN,
    FLOOR_DELETE_NON_AVAILABLE_ROOMS,
)
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...core.utils.room_occupancy import compute_room_occupancy_status, load_contracts_by_room_ids
from ...crud.crud_floor import crud_floors
from ...crud.crud_room import crud_rooms
from ...models.enums import RoomOccupancyStatus
from ...models.floor import Floor
from ...schemas.floor import FloorCreate, FloorCreateInternal, FloorRead, FloorUpdate
from ...schemas.room import RoomReadRow

router = APIRouter(prefix="/floors", tags=["floors"], dependencies=[Depends(get_current_staff)])


@router.post("", response_model=FloorRead, status_code=201)
async def create_floor(
    request: Request,
    body: FloorCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    created = await crud_floors.create(
        db=db,
        object=FloorCreateInternal.model_validate(body.model_dump()),
        schema_to_select=FloorRead,
    )
    if created is None:
        raise NotFoundException("Failed to create floor")
    return created


@router.get("", response_model=list[FloorRead])
async def list_floors(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[Any]:
    rows = await db.execute(select(Floor).where(Floor.deleted_at.is_(None)))
    return [FloorRead.model_validate(f) for f in rows.scalars().all()]


@router.get("/{floor_id}", response_model=FloorRead)
async def get_floor(
    request: Request,
    floor_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_floors.get(db=db, id=floor_id, deleted_at__is=None, schema_to_select=FloorRead)
    if row is None:
        raise NotFoundException("Floor not found")
    return row


@router.patch("/{floor_id}")
async def update_floor(
    request: Request,
    floor_id: UUID,
    values: FloorUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    existing = await crud_floors.get(db=db, id=floor_id, deleted_at__is=None, schema_to_select=FloorRead)
    if existing is None:
        raise NotFoundException("Floor not found")

    payload = values.model_dump(exclude_unset=True)
    nullable = {"description"}
    payload = {k: v for k, v in payload.items() if v is not None or k in nullable}
    if not payload:
        return {"message": "Nothing to update"}

    payload["updated_at"] = datetime.now(UTC)
    await crud_floors.update(db=db, object=payload, id=floor_id)
    return {"message": "Floor updated"}


@router.delete("/{floor_id}")
async def delete_floor(
    request: Request,
    floor_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_floors.exists(db=db, id=floor_id, deleted_at__is=None):
        raise NotFoundException("Floor not found")

    rooms_result = await crud_rooms.get_multi(
        db=db,
        schema_to_select=RoomReadRow,
        limit=None,
        deleted_at__is=None,
        return_total_count=False,
        floor_id=floor_id,
    )
    rooms = rooms_result["data"]
    if rooms:
        today = datetime.now(UTC).date()
        contracts_by_room = await load_contracts_by_room_ids(db, [r["id"] for r in rooms])
        for row in rooms:
            occupancy_status = compute_room_occupancy_status(
                today, contracts_by_room.get(row["id"], [])
            )
            if occupancy_status != RoomOccupancyStatus.AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": FLOOR_DELETE_NON_AVAILABLE_ROOMS,
                        "message": API_ERROR_MESSAGES_EN[FLOOR_DELETE_NON_AVAILABLE_ROOMS],
                    },
                )

        for row in rooms:
            await crud_rooms.delete(db=db, id=row["id"])

    await crud_floors.delete(db=db, id=floor_id)
    return {"message": "Floor deleted"}
