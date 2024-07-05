from typing import Optional

from fastapi import Depends, Request, exceptions
from fastapi_users import BaseUserManager, FastAPIUsers, exceptions, IntegerIDMixin
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users.db import SQLAlchemyUserDatabase

from app import schemas
from app.db import User, get_user_db

SECRET = "Some_SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    user_db_model = User
    verification_token_secret = SECRET

    async def create(
        self,
        user_create: schemas.UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        created_user = await self.user_db.create(user_create.dict())
        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

jwt_authentication = JWTStrategy(secret=SECRET, lifetime_seconds=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers(get_user_manager, [auth_backend])


current_active_user = fastapi_users.current_user(active=True)



