import uvicorn
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

from app.db import get_db
from app.exceptions import AddClientPanelError
from app.models import Protocol, User, Server
from app.payment.router import rout
from app.permissions import superuser_only
from app.schemas import AuthData, ServerRequest, ServerResponse, ClientResponse

from app.schemas import Protocol as ProtocolIn
from app.schemas import (ProtocolOut, SimpleAuthData, UserCreate, UserRead,
                         UserUpdate)
from app.users import current_active_user, fastapi_users
from app.utils import (
    extract_user_id, generate_custom_token, get_user_from_db,
    simple_get_user_from_db, validate_data_check_string, validate_init_data,
    create_new_client, get_most_unloaded_server, get_key_params,
    create_vless_key, server_user_count_increment
)
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv('BOT_TOKEN')

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.username}!"}


@router.get("/some-endpoint")
async def some_route():
    return {"message": "Hello!"}


@router.post("/client/", response_model=ClientResponse, tags=["client"])
async def create_client(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    server = await get_most_unloaded_server(db)
    if not server:
        raise HTTPException(
            status_code=500,
            detail="Find server Error"
        )
    tg_id = user.tg_id
    try:
        new_client_dict = await create_new_client(tg_id, server)
    except AddClientPanelError as e:
        raise HTTPException(status_code=500, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred)"
        )
    await server_user_count_increment(server, db)
    params = get_key_params(new_client_dict, server)

    if key := create_vless_key(params):
        return {"success": True, "vless_key": key}
    else:
        raise HTTPException(status_code=500, detail="Key generation error(")


@router.post("/server/", tags=["server"])
async def add_server(
    server: ServerRequest,
    user: dict = Depends(superuser_only),
    db: AsyncSession = Depends(get_db),
):
    db_server = Server(**server.dict())
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server


@router.get("/server/", response_model=List[ServerResponse], tags=["server"])
async def get_servers(
    user: dict = Depends(superuser_only),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Server))
    return result.scalars().all()


@router.get("/admin/")
async def read_admin_data(user: dict = Depends(superuser_only)):
    return {"msg": "This is admin data", "user": user}


@router.post("/auth", tags=["auth"])
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


@router.post("/simple-auth", tags=["auth"])
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
app.include_router(rout)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        log_level="info",
        reload=True,
        port=8080
    )
