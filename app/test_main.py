import os
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.app import get_db, app, BASE_DIR
from app.db import Base, engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import User
from app.utils import generate_custom_token, get_user_from_db

TEST_DB_PATH = os.path.join(BASE_DIR, "test.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

TestEngine = create_async_engine(TEST_DATABASE_URL, echo=True)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TestEngine,
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
        async with TestEngine.begin() as conn:
            # Создаем таблицы перед тестами
            await conn.run_sync(Base.metadata.create_all)
        yield client
        async with TestEngine.begin() as conn:
            # Удаляем таблицы после тестов
            await conn.run_sync(Base.metadata.drop_all)
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)


@pytest_asyncio.fixture(scope="module")
async def create_test_user(async_client):
    async with TestSessionLocal() as session:
        # Создаем тестового пользователя
        user = User(tg_id=20, username="TEST_USER", full_name="TEST_FULL_NAME")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture(scope="module")
async def auth_token(create_test_user):
    # Создаем токен для тестового пользователя
    access_token = await generate_custom_token(create_test_user)
    return access_token.get('token')


@pytest.mark.asyncio
async def test_generate_custom_token(create_test_user):
    access_token = await generate_custom_token(create_test_user)
    assert "token" in access_token


@pytest.mark.asyncio
async def test_get_user_from_db():
    user_dict = {
        "id": 800,
        "username": "TEST_USERNAME",
        "first_name": "TEST_FIRST_NAME",
        "last_name": "TEST_LAST_NAME"
    }
    async with TestSessionLocal() as session:
        user = await get_user_from_db(user_dict, session)
    assert isinstance(user, User)


@pytest.mark.asyncio
async def test_create_payment(async_client, auth_token):
    """Authenticated user creates payment."""
    response = await async_client.post(
        "/payment",
        json={
            "description": "string",
            "amount": 20,
            "user_id": 1,
            "plan_id": 1,
            "outstanding_balance": 0
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


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
