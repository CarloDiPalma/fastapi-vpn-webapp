from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import Literal

from app.payment.models import StatusEnum


class PaymentRequest(BaseModel):
    description: Optional[str]
    tariff_id: int


class PaymentResponse(PaymentRequest):
    id: int
    user_id: int
    tariff_id: int
    created_at: datetime
    outstanding_balance: int
    amount: str
    payment_url: str
    status: Literal[StatusEnum.succeeded, StatusEnum.created]
    payment_uuid: str


class Tariff(BaseModel):
    name: str
    price: int
    days: int
    description: Optional[str]


class TariffOut(Tariff):
    id: int
