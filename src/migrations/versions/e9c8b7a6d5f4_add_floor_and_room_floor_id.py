"""Add floor table; room.floor_id replaces room.floor.

Revision ID: e9c8b7a6d5f4
Revises: 7f3a2b1c4d5e
Create Date: 2026-04-02

"""

from collections.abc import Sequence
from typing import Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID

revision: str = "e9c8b7a6d5f4"
down_revision: Union[str, None] = "7f3a2b1c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "floor",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("floor_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("floor_number", name="uq_floor_floor_number"),
    )

    op.add_column("room", sa.Column("floor_id", UUID(as_uuid=True), nullable=True))

    connection = op.get_bind()
    distinct = connection.execute(text("SELECT DISTINCT floor FROM room")).fetchall()
    for (floor_num,) in distinct:
        floor_uuid = uuid4()
        connection.execute(
            text(
                "INSERT INTO floor (id, name, floor_number, description, created_at, updated_at, deleted_at) "
                "VALUES (:id, :name, :floor_number, NULL, NOW(), NOW(), NULL)"
            ),
            {"id": floor_uuid, "name": f"Floor {floor_num}", "floor_number": floor_num},
        )
        connection.execute(
            text("UPDATE room SET floor_id = :floor_id WHERE floor = :floor_num"),
            {"floor_id": floor_uuid, "floor_num": floor_num},
        )

    op.alter_column("room", "floor_id", nullable=False)
    op.drop_column("room", "floor")
    op.create_foreign_key("room_floor_id_fkey", "room", "floor", ["floor_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("room_floor_id_fkey", "room", type_="foreignkey")
    op.add_column("room", sa.Column("floor", sa.Integer(), nullable=True))

    connection = op.get_bind()
    connection.execute(
        text("""
            UPDATE room AS r
            SET floor = f.floor_number
            FROM floor AS f
            WHERE r.floor_id = f.id
        """)
    )

    op.alter_column("room", "floor", nullable=False)
    op.drop_column("room", "floor_id")
    op.drop_table("floor")
