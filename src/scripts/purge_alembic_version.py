"""Clear the ``alembic_version`` table (remove recorded migration revisions).

Use when you are replacing the migration chain or rebuilding the database schema.
This does **not** drop application tables. Typical flow:

1. Drop application tables (or full schema reset in dev).
2. Run this script: ``uv run python -m scripts.purge_alembic_version`` (from ``src``).
3. ``uv run python -m alembic upgrade head`` (from ``src``).

If ``alembic_version`` does not exist yet, this command will fail until the table is
created by Alembic or you can skip this step on a brand-new database.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import text

_SRC_ROOT = Path(__file__).resolve().parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from app.core.db.database import local_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    async with local_session() as session:
        await session.execute(text("DELETE FROM alembic_version"))
        await session.commit()
        logger.info("Purged alembic_version.")


if __name__ == "__main__":
    asyncio.run(main())
