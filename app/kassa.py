import os
import uuid

from yookassa import Payment, Configuration

from dotenv import load_dotenv

load_dotenv()

SHOP_ID = os.getenv('shopid')
SECRET_KEY = os.getenv('SECRET_KEY')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY


def create(amount, chat_id):
    id_key = str(uuid.uuid4())

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/roquentin_bot"
        },
        "capture": True,
        "metadata": {
            'chat_id': chat_id
        },
        "description": "Тестовый Заказ №1"
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id

