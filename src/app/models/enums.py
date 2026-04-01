from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"


class ContractStatus(StrEnum):
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"
    COMPLETED = "COMPLETED"
