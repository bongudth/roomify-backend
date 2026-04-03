from collections import defaultdict
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.contract import Contract
from ...models.enums import ContractStatus, RoomOccupancyStatus

# Days within which a move-out or move-in is considered "soon" for status flags.
SOON_DAYS = 30


def _effective_end(contract: Contract) -> date:
    return contract.terminated_at if contract.terminated_at is not None else contract.end_date


def _covers(contract: Contract, on_day: date) -> bool:
    if contract.status != ContractStatus.ACTIVE:
        return False
    end = _effective_end(contract)
    return contract.start_date <= on_day <= end


def compute_room_occupancy_status(on_day: date, contracts: list[Contract]) -> RoomOccupancyStatus:
    covering = [c for c in contracts if _covers(c, on_day)]
    if covering:
        for c in covering:
            days_left = (_effective_end(c) - on_day).days
            if 0 <= days_left <= SOON_DAYS:
                return RoomOccupancyStatus.VACATING_SOON
        return RoomOccupancyStatus.OCCUPIED

    future_active = [c for c in contracts if c.status == ContractStatus.ACTIVE and c.start_date > on_day]
    if future_active:
        min_days_until_start = min((c.start_date - on_day).days for c in future_active)
        if min_days_until_start <= SOON_DAYS:
            return RoomOccupancyStatus.INCOMING_TENANT

    return RoomOccupancyStatus.AVAILABLE


async def load_contracts_by_room_ids(db: AsyncSession, room_ids: list[UUID]) -> dict[UUID, list[Contract]]:
    if not room_ids:
        return {}
    result = await db.execute(
        select(Contract).where(
            Contract.room_id.in_(room_ids),
            Contract.deleted_at.is_(None),
        )
    )
    rows = result.scalars().all()
    by_room: dict[UUID, list[Contract]] = defaultdict(list)
    for contract in rows:
        by_room[contract.room_id].append(contract)
    return by_room
