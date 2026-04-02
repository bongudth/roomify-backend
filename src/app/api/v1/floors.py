from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ...crud.crud_floor import crud_floors
from ...crud.crud_room import crud_rooms
from ...schemas.floor import FloorCreate, FloorCreateInternal, FloorRead, FloorUpdate

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
    result = await crud_floors.get_multi(
        db=db,
        limit=None,
        is_deleted=False,
        return_total_count=False,
    )
    return result["data"]


@router.get("/{floor_id}", response_model=FloorRead)
async def get_floor(
    request: Request,
    floor_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_floors.get(db=db, id=floor_id, is_deleted=False, schema_to_select=FloorRead)
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
    existing = await crud_floors.get(db=db, id=floor_id, is_deleted=False, schema_to_select=FloorRead)
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
    if not await crud_floors.exists(db=db, id=floor_id, is_deleted=False):
        raise NotFoundException("Floor not found")

    if await crud_rooms.exists(db=db, floor_id=floor_id, is_deleted=False):
        raise BadRequestException("Cannot delete a floor that still has rooms. Remove or reassign rooms first.")

    await crud_floors.delete(db=db, id=floor_id)
    return {"message": "Floor deleted"}
