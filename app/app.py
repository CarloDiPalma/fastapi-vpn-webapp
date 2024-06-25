from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db import User, create_db_and_tables, async_session_maker
from app.models import Protocol
from app.schemas import (
    UserCreate, UserRead, UserUpdate, Protocol as ProtocolSchema
)
from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

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


@app.post("/protocol", response_model=ProtocolSchema)
async def create_book(protocol: ProtocolSchema, db: Session = Depends(get_db)):
    db_protocol = Protocol(name=protocol.name)
    db.add(db_protocol)
    await db.commit()
    await db.refresh(db_protocol)
    return db_protocol

# @app.get("/books/", response_model=List[schemas.Book])
# def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     books = db.query(models.Book).offset(skip).limit(limit).all()
#     return books


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
