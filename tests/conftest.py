from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.app.core.config import settings
from src.app.main import app
from src.app.models.enums import UserRole

DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_SYNC_PREFIX

sync_engine = create_engine(DATABASE_PREFIX + DATABASE_URI)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


fake = Faker()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as _client:
        yield _client
    app.dependency_overrides = {}
    sync_engine.dispose()


@pytest.fixture
def db() -> Generator[Session, Any, None]:
    session = local_session()
    yield session
    session.close()


def override_dependency(dependency: Callable[..., Any], mocked_response: Any) -> None:
    app.dependency_overrides[dependency] = lambda: mocked_response


@pytest.fixture
def mock_db():
    """Mock database session for unit tests."""
    return Mock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for unit tests."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis


@pytest.fixture
def shared_user_identity():
    return {
        "id": uuid4(),
        "name": fake.name(),
        "email": fake.email(),
    }


@pytest.fixture
def sample_user_data():
    """Generate sample user data for tests."""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "password": fake.password(),
    }


@pytest.fixture
def sample_user_read(shared_user_identity):
    """Generate a sample UserRead object."""
    from src.app.schemas.user import UserRead

    return UserRead(
        id=shared_user_identity["id"],
        name=shared_user_identity["name"],
        email=shared_user_identity["email"],
        role=UserRole.MANAGER,
    )


@pytest.fixture
def current_user_dict(shared_user_identity):
    """Mock current user from auth dependency."""
    return {
        "id": shared_user_identity["id"],
        "email": shared_user_identity["email"],
        "name": shared_user_identity["name"],
        "role": UserRole.MANAGER,
    }
