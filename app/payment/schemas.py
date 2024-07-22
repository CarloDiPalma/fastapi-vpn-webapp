from pydantic import BaseModel
from datetime import datetime


class Payment(BaseModel):
    description: str
    amount: int
    user_id: int
    tariff_id: int
    outstanding_balance: int


class PaymentOut(Payment):
    id: int
    created_at: datetime
