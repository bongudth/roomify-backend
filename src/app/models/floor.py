from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .room import Room


class Floor(TimestampMixin, Base):
    __tablename__ = "floor"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)

    rooms: Mapped[list[Room]] = relationship(back_populates="floor", init=False)
