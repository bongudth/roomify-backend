"""Idempotent seed data for Roomify domain models.

Private values (password, seed user emails) come from ``src/.env`` via ``SeedSettings``.
All other demo rows are defined as constants below — not read from the environment.

Run from the ``src`` directory:

  uv run python -m scripts.seed_data

**After replacing the migration chain** (single initial revision), reset the database
schema and Alembic bookkeeping before upgrading:

1. Drop application tables (or ``DROP SCHEMA public CASCADE; CREATE SCHEMA public;`` in dev).
2. Purge revision rows: ``DELETE FROM alembic_version;`` (or drop the table).
3. ``uv run python -m alembic upgrade head`` (from ``src``).
4. Run this seed script.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

# Repo layout: ``src/app`` — ensure ``src`` is importable when running as ``python -m scripts.seed_data``
_SRC_ROOT = Path(__file__).resolve().parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from app.core.config import settings
from app.core.db.database import AsyncSession, local_session
from app.core.security import get_password_hash
from app.models import Bill, Contract, ContractTenant, Floor, Room, RoomType, Setting, Tenant, User
from app.models.enums import ContractStatus, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Demo seed content (not from .env) ---
OWNER_NAME = "Seed Owner"
MANAGER_NAME = "Seed Manager"

SETTING_ELECTRICITY_PRICE_PER_UNIT = Decimal("3500.0000")
SETTING_WATER_FEE_PER_PERSON = Decimal("100000.00")
SETTING_SERVICE_FEE_PER_PERSON = Decimal("50000.00")

ROOM_A_NAME = "101"
ROOM_B_NAME = "201"
FLOOR_1_NAME = "1"
FLOOR_1_DESCRIPTION: str | None = None
FLOOR_2_NAME = "2"
FLOOR_2_DESCRIPTION: str | None = None
ROOM_A_CAPACITY = 2
ROOM_B_CAPACITY = 3
ROOM_TYPE_STANDARD_NAME = "Standard double"
ROOM_TYPE_STANDARD_RENT = Decimal("4500000.00")
ROOM_TYPE_STANDARD_DESCRIPTION = "Two-person standard layout."
ROOM_TYPE_FAMILY_NAME = "Family suite"
ROOM_TYPE_FAMILY_RENT = Decimal("5200000.00")
ROOM_TYPE_FAMILY_DESCRIPTION = "Larger unit for families."
ROOM_A_DESCRIPTION = "Corner room, street view."
ROOM_B_DESCRIPTION = "Family-sized unit."

TENANT_1_FULL_NAME = "Nguyen Van An"
TENANT_1_PHONE = "0901000001"
TENANT_1_ID_NUMBER = "079099001234"
TENANT_2_FULL_NAME = "Tran Thi Binh"
TENANT_2_PHONE = "0901000002"
TENANT_2_ID_NUMBER = "079099005678"

CONTRACT_START_DATE = date(2026, 1, 1)
CONTRACT_END_DATE = date(2026, 12, 31)
CONTRACT_DURATION_MONTHS = 12
CONTRACT_NOTE = "Seed contract for room A-101."

BILL_MONTH = 4
BILL_YEAR = 2026
BILL_ELECTRICITY_USAGE = Decimal("120.5000")
BILL_ELECTRICITY_UNIT_PRICE_SNAPSHOT = Decimal("3500.0000")
BILL_WATER_FEE_PER_PERSON_SNAPSHOT = Decimal("100000.00")
BILL_SERVICE_FEE_PER_PERSON_SNAPSHOT = Decimal("50000.00")


def _not_deleted(model):
    return model.deleted_at.is_(None)


async def seed_setting(session: AsyncSession) -> None:
    result = await session.execute(select(Setting).where(_not_deleted(Setting)).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Setting row already present; skipping.")
        return
    session.add(
        Setting(
            electricity_price_per_unit=SETTING_ELECTRICITY_PRICE_PER_UNIT,
            water_fee_per_person=SETTING_WATER_FEE_PER_PERSON,
            service_fee_per_person=SETTING_SERVICE_FEE_PER_PERSON,
        )
    )
    await session.flush()
    logger.info("Seeded setting defaults.")


async def seed_users(session: AsyncSession) -> None:
    hashed_password = get_password_hash(settings.SEED_PASSWORD.get_secret_value())

    result = await session.execute(
        select(User).where(User.email == settings.SEED_OWNER_EMAIL, _not_deleted(User))
    )
    owner = result.scalar_one_or_none()
    if owner is None:
        session.add(
            User(
                name=OWNER_NAME,
                email=settings.SEED_OWNER_EMAIL,
                hashed_password=hashed_password,
                role=UserRole.OWNER,
            )
        )
        await session.flush()
        logger.info("Created seed owner user.")
    else:
        logger.info("Seed owner user already exists.")

    result = await session.execute(
        select(User).where(User.email == settings.SEED_MANAGER_EMAIL, _not_deleted(User))
    )
    manager = result.scalar_one_or_none()
    if manager is None:
        session.add(
            User(
                name=MANAGER_NAME,
                email=settings.SEED_MANAGER_EMAIL,
                hashed_password=hashed_password,
                role=UserRole.MANAGER,
            )
        )
        await session.flush()
        logger.info("Created seed manager user.")
    else:
        logger.info("Seed manager user already exists.")


async def _ensure_floor_by_name(
    session: AsyncSession,
    name: str,
    description: str | None,
) -> Floor:
    result = await session.execute(
        select(Floor).where(Floor.name == name, _not_deleted(Floor)).limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = Floor(name=name, description=description)
        session.add(row)
        await session.flush()
        logger.info("Created floor %r.", name)
        return row
    updated = False
    if row.description != description:
        row.description = description
        updated = True
    if updated:
        await session.flush()
        logger.info("Updated floor %r metadata.", name)
    else:
        logger.info("Floor %r already exists.", name)
    return row


async def _ensure_room_type_by_name(
    session: AsyncSession,
    name: str,
    monthly_rent: Decimal,
    description: str | None,
) -> RoomType:
    result = await session.execute(select(RoomType).where(RoomType.name == name).limit(1))
    row = result.scalar_one_or_none()
    if row is None:
        row = RoomType(name=name, monthly_rent=monthly_rent, description=description)
        session.add(row)
        await session.flush()
        logger.info("Created room type %r.", name)
        return row
    updated = False
    if row.monthly_rent != monthly_rent:
        row.monthly_rent = monthly_rent
        updated = True
    if row.description != description:
        row.description = description
        updated = True
    if updated:
        await session.flush()
        logger.info("Updated room type %r metadata.", name)
    else:
        logger.info("Room type %r already exists.", name)
    return row


async def seed_rooms(session: AsyncSession) -> tuple[Room, Room]:
    floor_for_a = await _ensure_floor_by_name(session, FLOOR_1_NAME, FLOOR_1_DESCRIPTION)
    floor_for_b = await _ensure_floor_by_name(session, FLOOR_2_NAME, FLOOR_2_DESCRIPTION)
    type_standard = await _ensure_room_type_by_name(
        session, ROOM_TYPE_STANDARD_NAME, ROOM_TYPE_STANDARD_RENT, ROOM_TYPE_STANDARD_DESCRIPTION
    )
    type_family = await _ensure_room_type_by_name(
        session, ROOM_TYPE_FAMILY_NAME, ROOM_TYPE_FAMILY_RENT, ROOM_TYPE_FAMILY_DESCRIPTION
    )

    result = await session.execute(
        select(Room).where(Room.name == ROOM_A_NAME, _not_deleted(Room))
    )
    room_a = result.scalar_one_or_none()
    if room_a is None:
        room_a = Room(
            name=ROOM_A_NAME,
            floor_id=floor_for_a.id,
            room_type_id=type_standard.id,
            capacity=ROOM_A_CAPACITY,
            description=ROOM_A_DESCRIPTION,
        )
        session.add(room_a)
        await session.flush()
        logger.info("Created room %s.", ROOM_A_NAME)
    else:
        updated = False
        if room_a.floor_id != floor_for_a.id:
            room_a.floor_id = floor_for_a.id
            updated = True
        if room_a.room_type_id != type_standard.id:
            room_a.room_type_id = type_standard.id
            updated = True
        if room_a.capacity != ROOM_A_CAPACITY:
            room_a.capacity = ROOM_A_CAPACITY
            updated = True
        if room_a.description != ROOM_A_DESCRIPTION:
            room_a.description = ROOM_A_DESCRIPTION
            updated = True
        if updated:
            await session.flush()
            logger.info("Updated room %s metadata.", ROOM_A_NAME)
        else:
            logger.info("Room %s already exists.", ROOM_A_NAME)

    result = await session.execute(
        select(Room).where(Room.name == ROOM_B_NAME, _not_deleted(Room))
    )
    room_b = result.scalar_one_or_none()
    if room_b is None:
        room_b = Room(
            name=ROOM_B_NAME,
            floor_id=floor_for_b.id,
            room_type_id=type_family.id,
            capacity=ROOM_B_CAPACITY,
            description=ROOM_B_DESCRIPTION,
        )
        session.add(room_b)
        await session.flush()
        logger.info("Created room %s.", ROOM_B_NAME)
    else:
        updated = False
        if room_b.floor_id != floor_for_b.id:
            room_b.floor_id = floor_for_b.id
            updated = True
        if room_b.room_type_id != type_family.id:
            room_b.room_type_id = type_family.id
            updated = True
        if room_b.capacity != ROOM_B_CAPACITY:
            room_b.capacity = ROOM_B_CAPACITY
            updated = True
        if room_b.description != ROOM_B_DESCRIPTION:
            room_b.description = ROOM_B_DESCRIPTION
            updated = True
        if updated:
            await session.flush()
            logger.info("Updated room %s metadata.", ROOM_B_NAME)
        else:
            logger.info("Room %s already exists.", ROOM_B_NAME)

    return room_a, room_b


async def seed_tenants(session: AsyncSession) -> tuple[Tenant, Tenant]:
    result = await session.execute(
        select(Tenant).where(Tenant.id_number == TENANT_1_ID_NUMBER, _not_deleted(Tenant))
    )
    t1 = result.scalar_one_or_none()
    if t1 is None:
        t1 = Tenant(
            full_name=TENANT_1_FULL_NAME,
            phone=TENANT_1_PHONE,
            id_number=TENANT_1_ID_NUMBER,
        )
        session.add(t1)
        await session.flush()
        logger.info("Created tenant %s.", TENANT_1_ID_NUMBER)
    else:
        logger.info("Tenant %s already exists.", TENANT_1_ID_NUMBER)

    result = await session.execute(
        select(Tenant).where(Tenant.id_number == TENANT_2_ID_NUMBER, _not_deleted(Tenant))
    )
    t2 = result.scalar_one_or_none()
    if t2 is None:
        t2 = Tenant(
            full_name=TENANT_2_FULL_NAME,
            phone=TENANT_2_PHONE,
            id_number=TENANT_2_ID_NUMBER,
        )
        session.add(t2)
        await session.flush()
        logger.info("Created tenant %s.", TENANT_2_ID_NUMBER)
    else:
        logger.info("Tenant %s already exists.", TENANT_2_ID_NUMBER)

    return t1, t2


async def seed_contract_and_links(
    session: AsyncSession,
    room_a: Room,
    tenant_a: Tenant,
    tenant_b: Tenant,
) -> None:
    start = CONTRACT_START_DATE
    result = await session.execute(
        select(Contract).where(
            Contract.room_id == room_a.id,
            Contract.start_date == start,
            _not_deleted(Contract),
        )
    )
    contract = result.scalar_one_or_none()
    if contract is None:
        contract = Contract(
            room_id=room_a.id,
            start_date=CONTRACT_START_DATE,
            end_date=CONTRACT_END_DATE,
            duration_months=CONTRACT_DURATION_MONTHS,
            monthly_rent_snapshot=ROOM_TYPE_STANDARD_RENT,
            status=ContractStatus.ACTIVE,
            note=CONTRACT_NOTE,
        )
        session.add(contract)
        await session.flush()
        logger.info("Created seed contract for %s.", ROOM_A_NAME)
    else:
        logger.info("Seed contract for %s already exists.", ROOM_A_NAME)

    for tenant in (tenant_a, tenant_b):
        result = await session.execute(
            select(ContractTenant).where(
                ContractTenant.contract_id == contract.id,
                ContractTenant.tenant_id == tenant.id,
                _not_deleted(ContractTenant),
            )
        )
        if result.scalar_one_or_none() is None:
            session.add(ContractTenant(contract_id=contract.id, tenant_id=tenant.id))
            logger.info("Linked tenant %s to seed contract.", tenant.id)
        else:
            logger.info("Contract–tenant link for %s already exists.", tenant.id)

    await session.flush()


async def seed_bill(session: AsyncSession, room_a: Room) -> None:
    start = CONTRACT_START_DATE
    result = await session.execute(
        select(Contract).where(
            Contract.room_id == room_a.id,
            Contract.start_date == start,
            _not_deleted(Contract),
        )
    )
    contract = result.scalar_one_or_none()
    if contract is None:
        logger.warning("No contract for bill seed; skipping bill.")
        return

    result = await session.execute(
        select(Bill).where(
            Bill.room_id == room_a.id,
            Bill.contract_id == contract.id,
            Bill.month == BILL_MONTH,
            Bill.year == BILL_YEAR,
            _not_deleted(Bill),
        )
    )
    if result.scalar_one_or_none() is not None:
        logger.info(
            "Seed bill for %s-%02d already exists.",
            BILL_YEAR,
            BILL_MONTH,
        )
        return

    session.add(
        Bill(
            room_id=room_a.id,
            contract_id=contract.id,
            month=BILL_MONTH,
            year=BILL_YEAR,
            electricity_usage=BILL_ELECTRICITY_USAGE,
            electricity_unit_price_snapshot=BILL_ELECTRICITY_UNIT_PRICE_SNAPSHOT,
            water_fee_per_person_snapshot=BILL_WATER_FEE_PER_PERSON_SNAPSHOT,
            service_fee_per_person_snapshot=BILL_SERVICE_FEE_PER_PERSON_SNAPSHOT,
            room_rent_snapshot=ROOM_TYPE_STANDARD_RENT,
            other_fee=Decimal("0.00"),
            other_fee_note=None,
            is_paid=False,
            paid_at=None,
        )
    )
    await session.flush()
    logger.info(
        "Created seed bill for %s-%02d.",
        BILL_YEAR,
        BILL_MONTH,
    )


async def seed_all(session: AsyncSession) -> None:
    await seed_setting(session)
    await seed_users(session)
    room_a, _room_b = await seed_rooms(session)
    tenant_a, tenant_b = await seed_tenants(session)
    await seed_contract_and_links(session, room_a, tenant_a, tenant_b)
    await seed_bill(session, room_a)


async def main() -> None:
    async with local_session() as session:
        try:
            await seed_all(session)
            await session.commit()
            logger.info("Seed completed successfully.")
        except Exception:
            await session.rollback()
            logger.exception("Seed failed.")
            raise


if __name__ == "__main__":
    asyncio.run(main())
