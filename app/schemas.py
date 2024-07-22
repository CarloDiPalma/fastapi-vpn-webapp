from datetime import datetime
from typing import Optional

from fastapi_users.schemas import BaseUserUpdate, CreateUpdateDictModel
from pydantic import BaseModel


class UserCreate(CreateUpdateDictModel):
    tg_id: int
    username: str
    full_name: str
    parent_id: Optional[int]
    protocol_id: Optional[int]
    tariff_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserRead(BaseModel):
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
