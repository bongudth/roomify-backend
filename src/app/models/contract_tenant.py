from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .contract import Contract
    from .tenant import Tenant


class ContractTenant(TimestampMixin, Base):
    __tablename__ = "contract_tenant"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    contract_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("contract.id"))
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tenant.id"))

    contract: Mapped[Contract] = relationship(back_populates="contract_tenants", init=False)
    tenant: Mapped[Tenant] = relationship(back_populates="contract_tenants", init=False)
