"""Machine-readable API error codes for client i18n.

Each entry is a stable ``error_code`` string and its canonical English message
(fallback for clients that do not map the code).
"""

FLOOR_DELETE_NON_AVAILABLE_ROOMS = "FLOOR_DELETE_NON_AVAILABLE_ROOMS"

API_ERROR_MESSAGES_EN: dict[str, str] = {
    FLOOR_DELETE_NON_AVAILABLE_ROOMS: (
        "Cannot delete this floor unless every room on it is available "
        "(not occupied, vacating soon, or expecting an incoming tenant)."
    ),
}
