import json
import hashlib
import hmac

from urllib.parse import unquote, parse_qs
from pydantic import BaseModel


class AuthData(BaseModel):
    data_check_string: str


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
        user_id = user_info.get('id')
        return user_id
    return None

