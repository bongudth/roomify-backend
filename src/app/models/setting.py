from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from .mixins import TimestampMixin


class Setting(TimestampMixin, Base):
    __tablename__ = "setting"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    electricity_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    water_fee_per_person: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    service_fee_per_person: Mapped[Decimal] = mapped_column(Numeric(14, 2))
