from datetime import datetime
from typing import TYPE_CHECKING, Generic

from fastapi_users.models import ID
from sqlalchemy import (TIMESTAMP, BigInteger, Boolean, Column, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class CustomSQLAlchemyBaseUserTable(Generic[ID]):
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"

    if TYPE_CHECKING:  # pragma: no cover
        id: ID
        is_active: bool
        is_superuser: bool
        is_verified: bool
    else:
        is_active: Mapped[bool] = mapped_column(
            Boolean, default=True, nullable=False
        )
        is_superuser: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )
        is_verified: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )


class User(CustomSQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tg_id: int = Column(BigInteger, unique=True, nullable=False)
    subscription: str = Column(
        String(length=1024), default='none', nullable=False
    )
    username: str = Column(String(length=1024), nullable=False)
    full_name: str = Column(String(length=1024), nullable=False)
    parent_id = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    protocol_id = mapped_column(
        Integer, ForeignKey("protocol.id"), nullable=True
    )
    plan_id = mapped_column(
        Integer, ForeignKey("plan.id"), nullable=True
    )
    plan = relationship('Plan')
    payments = relationship('Payment', back_populates='user')
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_trial: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    registered_at = Column(
        TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow
    )


class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True)
    ip: str = Column(
        String(length=100), nullable=True
    )
    password: str = Column(
        String(length=100), nullable=True
    )
    is_active: bool = Column(Boolean, default=False, nullable=False)
    description: str = Column(String(length=1024), nullable=True)
    user_count: int = Column(BigInteger, nullable=True)


class Protocol(Base):
    __tablename__ = 'protocol'

    id = Column(Integer, primary_key=True)
    name: str = Column(
        String(length=100), nullable=False
    )
