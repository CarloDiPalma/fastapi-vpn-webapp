import os
from typing import List
from urllib.parse import unquote
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db import User, async_session_maker
from app.models import Protocol
from app.permissions import superuser_only
from app.schemas import (
    UserCreate, UserRead, UserUpdate, Protocol as ProtocolIn, ProtocolOut
)
from app.users import auth_backend, current_active_user, fastapi_users, \
    jwt_authentication
from app.utils import AuthData, validate_data_check_string, validate_init_data

load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@app.post("/protocol", response_model=ProtocolOut)
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


@app.get("/protocol/", response_model=List[ProtocolOut])
async def get_protocols(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(Protocol).offset(skip).limit(limit))
    return result.scalars().all()


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.get("/admin/")
async def read_admin_data(user: dict = Depends(superuser_only)):
    return {"msg": "This is admin data", "user": user}


@app.post("/auth")
async def auth(data: AuthData):
    data_check_string = unquote(data.data_check_string)

    if not validate_data_check_string(data_check_string):
        raise HTTPException(
            status_code=400,
            detail="Invalid data_check_string format"
        )
    if validate_init_data(data_check_string, BOT_TOKEN):
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Wrong hash")


@app.post("/custom-token")
async def generate_custom_token(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).filter(User.tg_id == 200))
    user = result.scalars().first()
    token = await jwt_authentication.write_token(user)
    return {"token": token}


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )



