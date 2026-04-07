from fastcrud import FastCRUD

from ..models.tenant import Tenant
from ..schemas.tenant import (
    TenantCreateInternal,
    TenantDelete,
    TenantRead,
    TenantUpdate,
    TenantUpdateInternal,
)

CRUDTenant = FastCRUD[
    Tenant,
    TenantCreateInternal,
    TenantUpdate,
    TenantUpdateInternal,
    TenantDelete,
    TenantRead,
]
crud_tenants = CRUDTenant(Tenant)
