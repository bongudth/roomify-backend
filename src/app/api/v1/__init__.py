from fastapi import APIRouter

from .floors import router as floors_router
from .health import router as health_router
from .login import router as login_router
from .logout import router as logout_router
from .room_types import router as room_types_router
from .rooms import router as rooms_router
from .tenants import router as tenants_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(floors_router)
router.include_router(room_types_router)
router.include_router(rooms_router)
router.include_router(tenants_router)
router.include_router(users_router)
