from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser):
    pass


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    tg_id: int
    username: str
    full_name: str
    parent_id: Optional[int]
    protocol_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass