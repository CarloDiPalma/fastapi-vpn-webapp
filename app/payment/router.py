from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.payment.models import Payment
from app.users import current_active_user

from app.payment.schemas import Payment as PaymentIn

from fastapi import APIRouter

rout = APIRouter(prefix="/api")


@rout.post("/payment")
async def create_payment(
    payment: PaymentIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment
