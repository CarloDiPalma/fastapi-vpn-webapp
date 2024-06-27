from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db import User, create_db_and_tables, async_session_maker
from app.models import Protocol
from app.permissions import superuser_only
from app.schemas import (
    UserCreate, UserRead, UserUpdate, Protocol as ProtocolIn, ProtocolOut
)
from app.users import auth_backend, current_active_user, fastapi_users


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Not needed if you setup a migration system like Alembic
#     await create_db_and_tables()
#     yield


app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
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
