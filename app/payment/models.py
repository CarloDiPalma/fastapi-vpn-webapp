from datetime import datetime
from enum import Enum
from sqlalchemy import (
    TIMESTAMP, Column, ForeignKey, Integer, String, Enum as SQLAEnum
)
from sqlalchemy.orm import mapped_column, relationship

from app.db import Base
from app.models import User


class Tariff(Base):
    __tablename__ = 'tariff'

    id = Column(Integer, primary_key=True)
    name: str = Column(
        String(length=140), default='none', nullable=False
    )
    price: int = Column(Integer, nullable=False, default=199)
    days: int = Column(Integer, nullable=False, default=30)
    description: str = Column(String(length=1024), nullable=True)


class StatusEnum(str, Enum):
    succeeded = "succeeded"
    created = "created"


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    description: str = Column(
        String(length=128), nullable=True
    )
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow
    )
    amount: str = Column(
        String(length=50), nullable=False
    )

    user_id = mapped_column(
        Integer, ForeignKey("user.id")
    )
    user = relationship('User')
    tariff_id = mapped_column(
        Integer, ForeignKey("tariff.id")
    )
    outstanding_balance: int = Column(Integer)
    payment_uuid: str = Column(
        String(length=128), nullable=False
    )
    payment_url: str = Column(
        String(length=300), nullable=False
    )
    status = Column(SQLAEnum(StatusEnum), nullable=False)
