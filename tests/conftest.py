import os
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import BASE_DIR, app, get_db, User

from app.models import Base
from app.utils import generate_custom_token

TEST_DB_PATH = os.path.join(BASE_DIR, "test.sqlite3")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
test_engine = create_async_engine(
    TEST_DATABASE_URL, future=True, echo=True,
)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

API_PREFIX = '/api'


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
        async with test_engine.begin() as conn:
            print('Создаем таблицы перед тестами')
            await conn.run_sync(Base.metadata.create_all)
        yield client
        async with test_engine.begin() as conn:
            print('Удаляем таблицы после тестов')
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
