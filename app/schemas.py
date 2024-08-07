from datetime import datetime
from typing import Optional

from fastapi_users.schemas import BaseUserUpdate, CreateUpdateDictModel
from pydantic import BaseModel


class UserCreate(CreateUpdateDictModel):
    tg_id: int
    username: str
    full_name: str
    parent_id: Optional[int] = None
    protocol_id: Optional[int] = None
    tariff_id: Optional[int] = None


class UserRead(BaseModel):
    id: int
    username: str
    tg_id: int
    subscription: str
    full_name: str
    parent_id: Optional[int] = None
    protocol_id: Optional[int] = None
    tariff_id: Optional[int] = None
    is_active: bool
    is_trial: bool
    is_superuser: bool
    is_verified: bool
    registered_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseUserUpdate):
    id: int
    username: str
    tg_id: int
    subscription: str
    full_name: str
    parent_id: int
    protocol_id: int
    tariff_id: Optional[int]
    is_active: bool
    is_trial: bool
    is_superuser: bool
    is_verified: bool
    registered_at: datetime


class Protocol(BaseModel):
    name: str


class ProtocolOut(Protocol):
    id: int


class AuthData(BaseModel):
    data_check_string: str


class SimpleAuthData(BaseModel):
    id: int


class ServerRequest(BaseModel):
    name: str
    ip: str
    port_panel: str
    port_key: str
    short_id: str
    public_key: str
    vless_inbound_id: int
    password: str
    uri_path: str
    is_active: bool
    description: str
    user_count: int


class ServerResponse(ServerRequest):
    id: int


class ClientRequest(BaseModel):
    pass


class ClientResponse(ClientRequest):
    success: bool
    vless_key: str

