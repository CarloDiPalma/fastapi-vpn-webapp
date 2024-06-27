from fastapi import HTTPException, status, Depends
from app.users import current_active_user


class SuperuserChecker:
    def __call__(self, user=Depends(current_active_user)):
        print(dir(user))
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )


# Создание экземпляра зависимости
superuser_only = SuperuserChecker()
