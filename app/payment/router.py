from typing import List

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import User
from app.payment.kassa import create_yookassa_payment
from app.payment.models import Payment, Tariff, StatusEnum
from app.payment.schemas import Tariff as TariffIn, TariffOut, PaymentOut
from app.users import current_active_user

from app.payment.schemas import Payment as PaymentIn

from fastapi import APIRouter

rout = APIRouter(prefix="/api")


@rout.post("/payment", tags=["payment"], response_model=PaymentOut)
async def create_payment(
    payment: PaymentIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    user_id = user.id
    tg_id = user.tg_id
    tariff_id = payment.tariff_id
    description = payment.description
    result = await db.execute(select(Tariff).filter(Tariff.id == tariff_id))
    tariff = result.scalars().first()
    if tariff is None:
        raise HTTPException(status_code=404, detail="Tariff not found")
    amount = tariff.price
    payment_url, payment_uuid = create_yookassa_payment(
        amount, tg_id, description
    )
    db_payment = Payment(
        user_id=user_id, amount=amount, status=StatusEnum.created,
        payment_uuid=payment_uuid, outstanding_balance=0,
        payment_url=payment_url, **payment.dict()
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment


@rout.get("/tariff", response_model=List[TariffOut], tags=["payment"])
async def get_all_tariffs(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tariff))
    return result.scalars().all()


@rout.post("/tariff", response_model=TariffOut, tags=["payment"])
async def create_tariff(
    tariff: TariffIn,
    db: AsyncSession = Depends(get_db),
):
    db_tariff = Tariff(**tariff.dict())
    db.add(db_tariff)
    await db.commit()
    await db.refresh(db_tariff)
    return db_tariff


@rout.post("/payment-notification", tags=["payment"])
async def payment_notification(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    json_body = await request.json()
    print(json_body)
    return {"received_json": json_body}
