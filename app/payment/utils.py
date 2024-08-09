import os

from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Server
from app.payment.models import Payment
from app.utils import dict_to_api_string

load_dotenv()

COOKIE = os.getenv('COOKIE')


def parse_notification_data(json: dict) -> (dict, int):
    """Parse json data from Yookassa from payment notification endpoint."""
    obj = json.get("object")
    description = obj.get("description")
    status = obj.get("status")
    amount = obj.get("amount").get("value")
    payment_uuid = obj.get("id")
    metadata = obj.get("metadata")
    tariff_id = metadata.get("tariff_id")
    user_id = metadata.get("user_id")
    tg_id = metadata.get("tg_id")
    return {
        "description": description,
        "status": status,
        "amount": amount,
        "payment_uuid": payment_uuid,
        "tariff_id": tariff_id,
        "user_id": user_id
    }, tg_id


async def create_db_payment(json_body: dict, db: AsyncSession) -> (dict, int):
    """Create Payment object in db."""
    if not json_body:
        print('No JSON')
    payment_dict, tg_id = parse_notification_data(json_body)

    db_payment = Payment(
        **payment_dict,
        payment_url="None", outstanding_balance=1000
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return payment_dict, tg_id


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    return result.scalars().first()


async def get_server_by_id(db: AsyncSession, server_id: int) -> Server:
    result = await db.execute(
        select(Server).filter(User.id == server_id)
    )
    return result.scalars().first()


async def prolong_key(server: Server, tg_id: int):
    EDIT_CLIENT_API_PATH = "panel/api/inbounds/updateClient"
    client_uuid = None
    expiry_unix_time = 0
    settings = dict_to_api_string(client_uuid, tg_id, expiry_unix_time)


async def edit_client_panel_request(vless_inbound_id, settings, url):
    payload = {"id": vless_inbound_id, "settings": settings}
    headers = {
        'Accept': 'application/json',
        'Cookie': COOKIE
    }
    async with AsyncClient(verify=False) as client:
        response = await client.post(
            url, headers=headers, data=payload
        )
    print(response.text, "STATUS CODE: ", response.status_code)
    return response.status_code, response.json()
