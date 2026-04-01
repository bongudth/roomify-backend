"""Idempotent seed data for Roomify domain models.

Configuration is read from ``src/.env`` via ``app.core.config.settings`` (see ``SeedSettings``).

Run from the ``src`` directory:

  uv run python -m scripts.seed_data
"""

from __future__ import annotations

import asyncio
import logging
import sys
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
from app.models import Bill, Contract, ContractTenant, Room, Setting, Tenant, User
from app.models.enums import ContractStatus, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _not_deleted(model):
    return model.deleted_at.is_(None)


async def seed_setting(session: AsyncSession) -> None:
    result = await session.execute(select(Setting).where(_not_deleted(Setting)).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Setting row already present; skipping.")
        return
    session.add(
        Setting(
            electricity_price_per_unit=settings.SEED_SETTING_ELECTRICITY_PRICE_PER_UNIT,
            water_fee_per_person=settings.SEED_SETTING_WATER_FEE_PER_PERSON,
            service_fee_per_person=settings.SEED_SETTING_SERVICE_FEE_PER_PERSON,
        )
    )
    await session.flush()
    logger.info("Seeded setting defaults.")


async def seed_users(session: AsyncSession) -> None:
    hashed = get_password_hash(settings.SEED_PASSWORD.get_secret_value())

    result = await session.execute(
        select(User).where(User.email == settings.SEED_OWNER_EMAIL, _not_deleted(User))
    )
    owner = result.scalar_one_or_none()
    if owner is None:
        session.add(
            User(
                name=settings.SEED_OWNER_NAME,
                email=settings.SEED_OWNER_EMAIL,
                password=hashed,
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
                name=settings.SEED_MANAGER_NAME,
                email=settings.SEED_MANAGER_EMAIL,
                password=hashed,
                role=UserRole.MANAGER,
            )
        )
        await session.flush()
        logger.info("Created seed manager user.")
    else:
        logger.info("Seed manager user already exists.")


async def seed_rooms(session: AsyncSession) -> tuple[Room, Room]:
    result = await session.execute(
        select(Room).where(Room.name == settings.SEED_ROOM_A_NAME, _not_deleted(Room))
    )
    room_a = result.scalar_one_or_none()
    if room_a is None:
        room_a = Room(
            name=settings.SEED_ROOM_A_NAME,
            floor=settings.SEED_ROOM_A_FLOOR,
            capacity=settings.SEED_ROOM_A_CAPACITY,
            monthly_rent=settings.SEED_ROOM_A_MONTHLY_RENT,
            description=settings.SEED_ROOM_A_DESCRIPTION,
        )
        session.add(room_a)
        await session.flush()
        logger.info("Created room %s.", settings.SEED_ROOM_A_NAME)
    else:
        if room_a.floor != settings.SEED_ROOM_A_FLOOR:
            room_a.floor = settings.SEED_ROOM_A_FLOOR
            await session.flush()
            logger.info("Updated room %s floor to %s.", settings.SEED_ROOM_A_NAME, settings.SEED_ROOM_A_FLOOR)
        else:
            logger.info("Room %s already exists.", settings.SEED_ROOM_A_NAME)

    result = await session.execute(
        select(Room).where(Room.name == settings.SEED_ROOM_B_NAME, _not_deleted(Room))
    )
    room_b = result.scalar_one_or_none()
    if room_b is None:
        room_b = Room(
            name=settings.SEED_ROOM_B_NAME,
            floor=settings.SEED_ROOM_B_FLOOR,
            capacity=settings.SEED_ROOM_B_CAPACITY,
            monthly_rent=settings.SEED_ROOM_B_MONTHLY_RENT,
            description=settings.SEED_ROOM_B_DESCRIPTION,
        )
        session.add(room_b)
        await session.flush()
        logger.info("Created room %s.", settings.SEED_ROOM_B_NAME)
    else:
        if room_b.floor != settings.SEED_ROOM_B_FLOOR:
            room_b.floor = settings.SEED_ROOM_B_FLOOR
            await session.flush()
            logger.info("Updated room %s floor to %s.", settings.SEED_ROOM_B_NAME, settings.SEED_ROOM_B_FLOOR)
        else:
            logger.info("Room %s already exists.", settings.SEED_ROOM_B_NAME)

    return room_a, room_b


async def seed_tenants(session: AsyncSession) -> tuple[Tenant, Tenant]:
    result = await session.execute(
        select(Tenant).where(Tenant.id_number == settings.SEED_TENANT_1_ID_NUMBER, _not_deleted(Tenant))
    )
    t1 = result.scalar_one_or_none()
    if t1 is None:
        t1 = Tenant(
            full_name=settings.SEED_TENANT_1_FULL_NAME,
            phone=settings.SEED_TENANT_1_PHONE,
            id_number=settings.SEED_TENANT_1_ID_NUMBER,
        )
        session.add(t1)
        await session.flush()
        logger.info("Created tenant %s.", settings.SEED_TENANT_1_ID_NUMBER)
    else:
        logger.info("Tenant %s already exists.", settings.SEED_TENANT_1_ID_NUMBER)

    result = await session.execute(
        select(Tenant).where(Tenant.id_number == settings.SEED_TENANT_2_ID_NUMBER, _not_deleted(Tenant))
    )
    t2 = result.scalar_one_or_none()
    if t2 is None:
        t2 = Tenant(
            full_name=settings.SEED_TENANT_2_FULL_NAME,
            phone=settings.SEED_TENANT_2_PHONE,
            id_number=settings.SEED_TENANT_2_ID_NUMBER,
        )
        session.add(t2)
        await session.flush()
        logger.info("Created tenant %s.", settings.SEED_TENANT_2_ID_NUMBER)
    else:
        logger.info("Tenant %s already exists.", settings.SEED_TENANT_2_ID_NUMBER)

    return t1, t2


async def seed_contract_and_links(
    session: AsyncSession,
    room_a: Room,
    tenant_a: Tenant,
    tenant_b: Tenant,
) -> None:
    start = settings.SEED_CONTRACT_START_DATE
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
            start_date=settings.SEED_CONTRACT_START_DATE,
            end_date=settings.SEED_CONTRACT_END_DATE,
            duration_months=settings.SEED_CONTRACT_DURATION_MONTHS,
            monthly_rent_snapshot=room_a.monthly_rent,
            status=ContractStatus.ACTIVE,
            note=settings.SEED_CONTRACT_NOTE,
        )
        session.add(contract)
        await session.flush()
        logger.info("Created seed contract for %s.", settings.SEED_ROOM_A_NAME)
    else:
        logger.info("Seed contract for %s already exists.", settings.SEED_ROOM_A_NAME)

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
    start = settings.SEED_CONTRACT_START_DATE
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
            Bill.month == settings.SEED_BILL_MONTH,
            Bill.year == settings.SEED_BILL_YEAR,
            _not_deleted(Bill),
        )
    )
    if result.scalar_one_or_none() is not None:
        logger.info(
            "Seed bill for %s-%02d already exists.",
            settings.SEED_BILL_YEAR,
            settings.SEED_BILL_MONTH,
        )
        return

    session.add(
        Bill(
            room_id=room_a.id,
            contract_id=contract.id,
            month=settings.SEED_BILL_MONTH,
            year=settings.SEED_BILL_YEAR,
            electricity_usage=settings.SEED_BILL_ELECTRICITY_USAGE,
            electricity_unit_price_snapshot=settings.SEED_BILL_ELECTRICITY_UNIT_PRICE_SNAPSHOT,
            water_fee_per_person_snapshot=settings.SEED_BILL_WATER_FEE_PER_PERSON_SNAPSHOT,
            service_fee_per_person_snapshot=settings.SEED_BILL_SERVICE_FEE_PER_PERSON_SNAPSHOT,
            room_rent_snapshot=room_a.monthly_rent,
            other_fee=Decimal("0.00"),
            other_fee_note=None,
            is_paid=False,
            paid_at=None,
        )
    )
    await session.flush()
    logger.info(
        "Created seed bill for %s-%02d.",
        settings.SEED_BILL_YEAR,
        settings.SEED_BILL_MONTH,
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
