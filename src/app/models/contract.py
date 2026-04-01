from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .enums import ContractStatus
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .bill import Bill
    from .contract_tenant import ContractTenant
    from .room import Room


class Contract(TimestampMixin, Base):
    __tablename__ = "contract"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    room_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("room.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    duration_months: Mapped[int] = mapped_column(Integer)
    monthly_rent_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, native_enum=False, length=20),
        default=ContractStatus.ACTIVE,
    )
    terminated_at: Mapped[date | None] = mapped_column(Date, default=None)
    note: Mapped[str | None] = mapped_column(Text, default=None)

    room: Mapped[Room] = relationship(back_populates="contracts", init=False)
    contract_tenants: Mapped[list[ContractTenant]] = relationship(back_populates="contract", init=False)
    bills: Mapped[list[Bill]] = relationship(back_populates="contract", init=False)
