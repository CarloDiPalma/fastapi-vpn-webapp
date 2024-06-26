import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.app import get_db, app
from app.db import Base, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async with engine.begin() as conn:
            # Создаем таблицы перед тестами
            await conn.run_sync(Base.metadata.create_all)
        yield client
        async with engine.begin() as conn:
            # Удаляем таблицы после тестов
            await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_protocol(async_client):
    response = await async_client.post(
        "/protocol",
        json={"name": "Test Protocol"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Protocol"
    # assert "id" in data
