"""Drop floor.floor_number (use name only).

Revision ID: f2e1d0c9b8a7
Revises: e9c8b7a6d5f4
Create Date: 2026-04-02

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "f2e1d0c9b8a7"
down_revision: Union[str, None] = "e9c8b7a6d5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_floor_floor_number", "floor", type_="unique")
    op.drop_column("floor", "floor_number")


def downgrade() -> None:
    op.add_column("floor", sa.Column("floor_number", sa.Integer(), nullable=True))

    connection = op.get_bind()
    connection.execute(
        text("""
            WITH ranked AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS n
                FROM floor
            )
            UPDATE floor AS f
            SET floor_number = ranked.n
            FROM ranked
            WHERE f.id = ranked.id
        """)
    )

    op.alter_column("floor", "floor_number", nullable=False)
    op.create_unique_constraint("uq_floor_floor_number", "floor", ["floor_number"])
