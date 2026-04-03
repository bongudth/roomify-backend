from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"


class ContractStatus(StrEnum):
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"
    COMPLETED = "COMPLETED"


class RoomOccupancyStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    VACATING_SOON = "VACATING_SOON"
    INCOMING_TENANT = "INCOMING_TENANT"
