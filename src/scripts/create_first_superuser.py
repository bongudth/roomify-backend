"""Create the first admin user if missing (OWNER role). Run from ``src``: ``uv run python -m scripts.create_first_superuser``."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select

_SRC_ROOT = Path(__file__).resolve().parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from app.core.config import settings
from app.core.db.database import local_session
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_user() -> None:
    async with local_session() as session:
        result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        if result.scalar_one_or_none() is not None:
            logger.info("Admin user %s already exists.", settings.ADMIN_EMAIL)
            return

        session.add(
            User(
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.OWNER,
            )
        )
        await session.commit()
        logger.info("Admin user %s created successfully.", settings.ADMIN_EMAIL)


async def main() -> None:
    await create_first_user()


if __name__ == "__main__":
    asyncio.run(main())
