from fastapi import Depends, HTTPException, status

from app.users import current_active_user


class SuperuserChecker:
    def __call__(self, user=Depends(current_active_user)):
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )


# Создание экземпляра зависимости
superuser_only = SuperuserChecker()
