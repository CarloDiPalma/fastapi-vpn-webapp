from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Payment(BaseModel):
    description: str
    amount: int
    tariff_id: int
    outstanding_balance: int


class PaymentOut(Payment):
    id: int
    user_id: int
    created_at: datetime


class Tariff(BaseModel):
    name: str
    price: int
    days: int
    description: Optional[str]


class TariffOut(Tariff):
    id: int
