import os
import uuid

from dotenv import load_dotenv
from yookassa import Configuration, Payment

load_dotenv()

SHOP_ID = os.getenv('shopid')
SECRET_KEY_YOOKASSA = os.getenv('SECRET_KEY_YOOKASSA')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY_YOOKASSA


def create_yookassa_payment(amount, metadata: dict, description):
    id_key = str(uuid.uuid4())

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://vpntelegram.ru"
        },
        "capture": True,
        "metadata": {
            **metadata
        },
        "description": description
    }, id_key)
    print(payment.confirmation.confirmation_url, payment.id, payment.metadata)
    return payment.confirmation.confirmation_url, payment.id
