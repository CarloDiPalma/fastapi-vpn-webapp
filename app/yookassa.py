import os
import uuid

from yookassa import Configuration, Payment


from dotenv import load_dotenv

load_dotenv()

SHOP_ID = os.getenv('shopid')
SECRET_KEY = os.getenv('SECRET_KEY')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://www.example.com/return_url"
    },
    "capture": True,
    "description": "Заказ №1"
}, uuid.uuid4())