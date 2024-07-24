from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import User
from app.payment.models import Payment, Tariff
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
    db_payment = Payment(user_id=user.id, **payment.dict())
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
async def get_all_tariffs(
    tariff: TariffIn,
    db: AsyncSession = Depends(get_db),
):
    db_tariff = Tariff(**tariff.dict())
    db.add(db_tariff)
    await db.commit()
    await db.refresh(db_tariff)
    return db_tariff
