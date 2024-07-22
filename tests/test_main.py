import pytest
from app.utils import generate_custom_token, get_user_from_db, User
from tests.conftest import TestSessionLocal

API_PREFIX = '/api'


@pytest.mark.asyncio
async def test_generate_custom_token(create_test_user):
    access_token = await generate_custom_token(create_test_user)
    assert "token" in access_token


@pytest.mark.asyncio
async def test_get_user_from_db_function():
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
        API_PREFIX + "/payment",
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
        API_PREFIX + "/protocol",
        json={"name": "Test Protocol"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Protocol"
    assert "id" in data
