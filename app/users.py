from typing import Optional, Union, Dict

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.exc import IntegrityError

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
    ) -> Union[User, Dict[str, str]]:
        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        try:
            created_user = await self.user_db.create(user_dict)
        except IntegrityError as e:
            if 'UNIQUE constraint failed: user.tg_id' in str(e.orig):
                return {
                    "error": "Пользователь с таким tg_id уже существует"
                }

        await self.on_after_register(created_user, request)
        return created_user

    async def update(
        self,
        user_update: schemas.UserUpdate,
        user: User,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}."
              f"Verification token: {token}")


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db)
):
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
