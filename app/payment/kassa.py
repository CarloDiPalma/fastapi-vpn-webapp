import os
import uuid

from dotenv import load_dotenv
from yookassa import Configuration, Payment

load_dotenv()

SHOP_ID = os.getenv('shopid')
SECRET_KEY = os.getenv('SECRET_KEY')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY


def create_yookassa_payment(amount, tg_id, description):
    id_key = str(uuid.uuid4())

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/SupaVPN_bot"
        },
        "capture": True,
        "metadata": {
            "tg_id": tg_id
        },
        "description": description
    }, id_key)
    print(payment.confirmation.confirmation_url, payment.id)
    return payment.confirmation.confirmation_url, payment.id
