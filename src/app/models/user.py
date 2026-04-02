from uuid import UUID, uuid4

from sqlalchemy import Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from .enums import UserRole
from .mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default_factory=uuid4, init=False)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False, length=20), default=UserRole.MANAGER)
