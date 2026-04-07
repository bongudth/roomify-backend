from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Date, String, Text, Uuid
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
    address: Mapped[str | None] = mapped_column(Text, default=None)
    birthday: Mapped[date | None] = mapped_column(Date, default=None)
    email: Mapped[str | None] = mapped_column(String(255), default=None)

    contract_tenants: Mapped[list[ContractTenant]] = relationship(back_populates="tenant", init=False)
