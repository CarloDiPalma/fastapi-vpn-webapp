import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.app import get_db, app
from app.db import Base, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import User
from app.utils import generate_custom_token

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        async with engine.begin() as conn:
            # Создаем таблицы перед тестами
            await conn.run_sync(Base.metadata.create_all)
        yield client
        async with engine.begin() as conn:
            # Удаляем таблицы после тестов
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="module")
async def auth_token(async_client):
    async with TestSessionLocal() as session:
        # Создаем тестового пользователя
        user = User(tg_id=10, username="TEST_USER", full_name="TEST_FULL_NAME")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        # Создаем токен для этого пользователя
        access_token = await generate_custom_token(user)
        return access_token.get('token')


@pytest.mark.asyncio
async def test_create_protocol(async_client, auth_token):
    response = await async_client.post(
        "/protocol",
        json={"name": "Test Protocol"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Protocol"
    assert "id" in data
