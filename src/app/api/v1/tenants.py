from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_staff
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ...crud.crud_tenant import crud_tenants
from ...models.contract_tenant import ContractTenant
from ...schemas.tenant import TenantCreate, TenantCreateInternal, TenantRead, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"], dependencies=[Depends(get_current_staff)])

TENANT_NOT_FOUND = "Tenant not found"


@router.post("", response_model=TenantRead, status_code=201)
async def create_tenant(
    request: Request,
    body: TenantCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    created = await crud_tenants.create(
        db=db,
        object=TenantCreateInternal.model_validate(body.model_dump()),
        schema_to_select=TenantRead,
    )
    if created is None:
        raise NotFoundException("Failed to create tenant")
    return created


@router.get("", response_model=list[TenantRead])
async def list_tenants(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[Any]:
    result = await crud_tenants.get_multi(
        db=db,
        limit=None,
        schema_to_select=TenantRead,
        return_total_count=False,
        deleted_at__is=None,
    )
    return result["data"]


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    request: Request,
    tenant_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    row = await crud_tenants.get(db=db, id=tenant_id, deleted_at__is=None, schema_to_select=TenantRead)
    if row is None:
        raise NotFoundException(TENANT_NOT_FOUND)
    return row


@router.patch("/{tenant_id}")
async def update_tenant(
    request: Request,
    tenant_id: UUID,
    values: TenantUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    existing = await crud_tenants.get(db=db, id=tenant_id, deleted_at__is=None, schema_to_select=TenantRead)
    if existing is None:
        raise NotFoundException(TENANT_NOT_FOUND)

    payload = values.model_dump(exclude_unset=True)
    nullable = {"address", "birthday", "email"}
    payload = {k: v for k, v in payload.items() if v is not None or k in nullable}
    if not payload:
        return {"message": "Nothing to update"}

    payload["updated_at"] = datetime.now(UTC)
    await crud_tenants.update(db=db, object=payload, id=tenant_id)
    return {"message": "Tenant updated"}


@router.delete("/{tenant_id}")
async def delete_tenant(
    request: Request,
    tenant_id: UUID,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    if not await crud_tenants.exists(db=db, id=tenant_id, deleted_at__is=None):
        raise NotFoundException(TENANT_NOT_FOUND)

    link_result = await db.execute(
        select(ContractTenant.id).where(
            ContractTenant.tenant_id == tenant_id,
            ContractTenant.deleted_at.is_(None),
        ).limit(1)
    )
    if link_result.scalar_one_or_none() is not None:
        raise BadRequestException(
            "Cannot delete a tenant who is still linked to one or more contracts.",
        )

    await crud_tenants.delete(db=db, id=tenant_id)
    return {"message": "Tenant deleted"}
