from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .contract_tenant import ContractTenant


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenant"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(32))
    id_number: Mapped[str] = mapped_column(String(64))

    contract_tenants: Mapped[list[ContractTenant]] = relationship(back_populates="tenant", init=False)
