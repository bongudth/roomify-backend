"""Add tenant address, birthday, and email.

Revision ID: a3b2c1d0e9f8
Revises: f8e7d6c5b4a3
Create Date: 2026-04-03

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3b2c1d0e9f8"
down_revision: Union[str, None] = "f8e7d6c5b4a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenant", sa.Column("address", sa.Text(), nullable=True))
    op.add_column("tenant", sa.Column("birthday", sa.Date(), nullable=True))
    op.add_column("tenant", sa.Column("email", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("tenant", "email")
    op.drop_column("tenant", "birthday")
    op.drop_column("tenant", "address")
