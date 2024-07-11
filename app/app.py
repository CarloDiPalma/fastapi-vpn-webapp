import os
from pathlib import Path
from typing import List
from urllib.parse import unquote

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, APIRouter
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.db import User, async_session_maker, get_db
from app.models import Payment, Protocol
from app.permissions import superuser_only
from app.schemas import AuthData
from app.schemas import Payment as PaymentIn
from app.schemas import Protocol as ProtocolIn
from app.schemas import (ProtocolOut, SimpleAuthData, UserCreate, UserRead,
                         UserUpdate)
from app.users import current_active_user, fastapi_users
from app.utils import (extract_user_id, generate_custom_token,
                       get_user_from_db, simple_get_user_from_db,
                       validate_data_check_string, validate_init_data)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

BOT_TOKEN = os.getenv('BOT_TOKEN')
app = FastAPI()

router = APIRouter(prefix="/api")

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.post("/protocol", response_model=ProtocolOut)
async def create_protocol(
    protocol: ProtocolIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    db_protocol = Protocol(name=protocol.name)
    db.add(db_protocol)
    await db.commit()
    await db.refresh(db_protocol)
    return db_protocol


@router.get("/protocol/", response_model=List[ProtocolOut])
async def get_protocols(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Protocol).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/payment")
async def payment(
    payment: PaymentIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router.get("/some-endpoint")
async def some_route():
    return {"message": f"Hello!"}


@router.get("/admin/")
async def read_admin_data(user: dict = Depends(superuser_only)):
    return {"msg": "This is admin data", "user": user}


@router.post("/auth")
async def auth(
    data: AuthData,
    db: AsyncSession = Depends(get_db),
):
    data_check_string = unquote(data.data_check_string)

    if not validate_data_check_string(data_check_string):
        raise HTTPException(
            status_code=400,
            detail="Invalid data_check_string format"
        )
    if validate_init_data(data_check_string, BOT_TOKEN):
        user_info = extract_user_id(data_check_string)
        user = await get_user_from_db(user_info, db)
        response = await generate_custom_token(user)
        return response
    else:
        raise HTTPException(status_code=401, detail="Wrong hash")


@router.post("/simple-auth")
async def simple_auth(
    data: SimpleAuthData,
    db: AsyncSession = Depends(get_db)
):
    user_id = data.id
    user = await simple_get_user_from_db(user_id, db)
    response = await generate_custom_token(user)
    return response


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )

# Включаем основной маршрутизатор в приложение
app.include_router(router)