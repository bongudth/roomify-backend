"""Roomify domain models (user, room, tenant, contract, bill, setting).

Revision ID: 7f3a2b1c4d5e
Revises:
Create Date: 2026-04-01

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "7f3a2b1c4d5e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    op.create_table(
        "room",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("floor", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("monthly_rent", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tenant",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("id_number", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "setting",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("electricity_price_per_unit", sa.Numeric(14, 4), nullable=False),
        sa.Column("water_fee_per_person", sa.Numeric(14, 2), nullable=False),
        sa.Column("service_fee_per_person", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "contract",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("room_id", UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("monthly_rent_snapshot", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("terminated_at", sa.Date(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "contract_tenant",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["contract.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "bill",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("room_id", UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", UUID(as_uuid=True), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("electricity_usage", sa.Numeric(14, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("electricity_unit_price_snapshot", sa.Numeric(14, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("water_fee_per_person_snapshot", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("service_fee_per_person_snapshot", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("room_rent_snapshot", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("other_fee", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("other_fee_note", sa.Text(), nullable=True),
        sa.Column("is_paid", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["contract.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bill")
    op.drop_table("contract_tenant")
    op.drop_table("contract")
    op.drop_table("setting")
    op.drop_table("tenant")
    op.drop_table("room")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
