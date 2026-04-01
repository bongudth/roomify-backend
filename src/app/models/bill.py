from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .contract import Contract
    from .room import Room


class Bill(TimestampMixin, Base):
    __tablename__ = "bill"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    room_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("room.id"))
    contract_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("contract.id"))
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    electricity_usage: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=Decimal("0"))
    electricity_unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=Decimal("0"))
    water_fee_per_person_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    service_fee_per_person_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    room_rent_snapshot: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    other_fee: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    other_fee_note: Mapped[str | None] = mapped_column(Text, default=None)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    room: Mapped[Room] = relationship(back_populates="bills", init=False)
    contract: Mapped[Contract] = relationship(back_populates="bills", init=False)
