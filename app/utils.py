import json
import hashlib
import hmac

from urllib.parse import unquote, parse_qs

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from app.app import get_db
from app.models import User
from app.users import jwt_authentication





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
        print(user_info)
        # Извлекаем 'id' из JSON-объекта
        # user_id = user_info.get('id')
        # return user_id
        return user_info
    return None


async def get_user_from_db(
    user_info: dict,
    db: AsyncSession,
) -> User:
    tg_id = user_info['id']
    result = await db.execute(select(User).filter(User.tg_id == tg_id))
    user = result.scalars().first()
    if user:
        return user
    else:
        user = User(
            tg_id=tg_id, username=user_info['username'],
            full_name=user_info['first_name'] + user_info['last_name'],
            hashed_password='ds', email='asd@mail.com'
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def simple_get_user_from_db(pk: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).filter(User.id == pk))
    user = result.scalars().first()
    if user:
        return user


async def generate_custom_token(
    user: User
):
    token = await jwt_authentication.write_token(user)
    return {"token": token}
