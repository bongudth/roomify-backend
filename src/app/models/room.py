from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .bill import Bill
    from .contract import Contract
    from .floor import Floor
    from .room_type import RoomType


class Room(TimestampMixin, Base):
    __tablename__ = "room"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    name: Mapped[str] = mapped_column(String(255))
    floor_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("floor.id"))
    room_type_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("room_type.id"))
    capacity: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    floor: Mapped[Floor] = relationship(back_populates="rooms", init=False)
    room_type: Mapped[RoomType] = relationship(back_populates="rooms", init=False)
    contracts: Mapped[list[Contract]] = relationship(back_populates="room", init=False)
    bills: Mapped[list[Bill]] = relationship(back_populates="room", init=False)
