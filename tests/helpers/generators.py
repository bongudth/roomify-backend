from sqlalchemy.orm import Session

from src.app import models
from src.app.core.security import get_password_hash
from src.app.models.enums import UserRole
from tests.conftest import fake


def create_user(db: Session, is_super_user: bool = False) -> models.User:
    _user = models.User(
        name=fake.name(),
        email=fake.email(),
        hashed_password=get_password_hash(fake.password()),
        role=UserRole.OWNER if is_super_user else UserRole.MANAGER,
    )

    db.add(_user)
    db.commit()
    db.refresh(_user)

    return _user
