import hashlib
import hmac
import json
import os
import time
import uuid
from typing import Dict, Any

from urllib.parse import parse_qs, unquote
from uuid import UUID

from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Server
from app.users import jwt_authentication

load_dotenv()

COOKIE = os.getenv('COOKIE')


def validate_data_check_string(data_check_string: str) -> bool:
    try:
        data_check_array = data_check_string.split('&')
        data_dict = dict(item.split('=') for item in data_check_array)
        return 'auth_date' in data_dict and 'hash' in data_dict
    except ValueError:
        return False


def validate_init_data(init_data: str, bot_token: str):
    vals = {
        k: unquote(v) for k, v in [
            s.split('=', 1) for s in init_data.split('&')
        ]
    }
    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash'
    )
    secret_key = hmac.new(
        "WebAppData".encode(),
        bot_token.encode(),
        hashlib.sha256
    ).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
    return h.hexdigest() == vals['hash']


def extract_user_id(data_check_string):
    # Разбираем строку URL-параметров
    params = parse_qs(data_check_string)
    # Получаем значение параметра 'user'
    user_data = params.get('user', [None])[0]

    if user_data:
        # Декодируем URL-кодированную строку
        user_data = user_data.replace('%7B', '{').replace('%7D', '}').replace(
            '%22', '"').replace('%3A', ':').replace('%2C', ',')
        # Преобразуем строку в JSON-объект
        user_info = json.loads(user_data)
        # Извлекаем 'id' из JSON-объекта
        # user_id = user_info.get('id')
        # return user_id
        return user_info
    return None


async def get_user_from_db(user_info: dict, db: AsyncSession) -> User:
    """Get or create user instance from telegram data."""
    tg_id = user_info['id']
    result = await db.execute(select(User).filter(User.tg_id == tg_id))
    user = result.scalars().first()
    if user:
        return user
    else:
        user = User(
            tg_id=tg_id, username=user_info['username'],
            full_name=user_info['first_name'] + user_info['last_name']
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def simple_get_user_from_db(pk: int, db: AsyncSession) -> User:
    """Get User object for development and tests."""
    result = await db.execute(select(User).filter(User.id == pk))
    user = result.scalars().first()
    if user:
        return user


async def generate_custom_token(user: User):
    if user:
        token = await jwt_authentication.write_token(user)
        return {"token": token}


def generate_unixtime_for_days(days) -> int:
    current_time = time.time()
    ONE_DAY_SECONDS = 86400

    future_time = (current_time + days * ONE_DAY_SECONDS) * 1000
    return int(future_time)


async def create_new_client(
        tg_id: int, server: Server
) -> dict[str, UUID | str]:
    """Send request to panel to create new client."""
    new_uuid = uuid.uuid4()
    ip = server.ip
    port = server.port
    uri_path = server.uri_path
    ADD_CLIENT_API_PATH = "panel/api/inbounds/addClient"
    api_panel_url = f"https://{ip}:{port}/{uri_path}/{ADD_CLIENT_API_PATH}"
    TRIAL_DAYS = 3
    expiry_unix_time = generate_unixtime_for_days(TRIAL_DAYS)
    settings = dict_to_api_string(new_uuid, tg_id, expiry_unix_time)
    try:
        status_code, response_json = await add_client_panel_request(
            settings, api_panel_url
        )
        if status_code == 200 and response_json.get("success"):
            return {"new_client_uuid": new_uuid, "ip": ip}
    except:
        return {}


def get_key_params(base_dict: dict, server: Server) -> dict:
    additional_dict = {
        "public_key": server.public_key,
        "short_id": server.short_id,
        "port_key": server.port_key
    }
    base_dict.update(additional_dict)
    return base_dict


def create_vless_key(params: dict) -> str:
    uuid = params["new_client_uuid"]
    ip = params["ip"]
    port = params["port_key"]
    public_key = params["public_key"]
    short_id = params["short_id"]
    key = f"vless://{uuid}@{ip}:{port}?fp=chrome&pbk={public_key}&security" \
          f"=reality&sid={short_id}&sni=yahoo.com&spx=%2F&type=tcp#Salam_VPN" \
          f"-vless"
    return key


async def add_client_panel_request(settings, url):
    payload = {"id": 1, "settings": settings}
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


def dict_to_api_string(
        uuid: uuid.UUID, tg_id: int, expiry_unix_time: int, traffic_limit=0
) -> str:
    """Convert dict to MHSanaei panel API string format."""
    tg_id_str = str(tg_id) + ':Salam_VPN'
    input_dict = {"clients": [
        {"id": str(uuid), "alterId": 0, "email": tg_id_str, "limitIp": 2,
         "totalGB": traffic_limit, "expiryTime": expiry_unix_time,
         "enable": True, "tgId": "", "subId": ""}
    ]}
    json_string = json.dumps(input_dict, ensure_ascii=False)
    return json_string


async def get_most_unloaded_server(db: AsyncSession) -> Server:
    """Get server object with min user_count."""
    result = await db.execute(
        select(Server).order_by(asc(Server.user_count)).limit(1))
    return result.scalars().first()
