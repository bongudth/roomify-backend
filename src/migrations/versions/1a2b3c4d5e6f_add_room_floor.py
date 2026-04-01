"""Add floor to room.

Revision ID: 1a2b3c4d5e6f
Revises: 7f3a2b1c4d5e
Create Date: 2026-04-01

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, None] = "7f3a2b1c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add with a server default to backfill existing rows, then remove the default.
    op.add_column(
        "room",
        sa.Column("floor", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.alter_column("room", "floor", server_default=None)


def downgrade() -> None:
    op.drop_column("room", "floor")

