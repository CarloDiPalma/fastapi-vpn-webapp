from datetime import datetime
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, Integer, String)
from sqlalchemy.orm import mapped_column, relationship

from app.db import Base
from app.models import User


class Tariff(Base):
    __tablename__ = 'tariff'

    id = Column(Integer, primary_key=True)
    name: str = Column(
        String(length=1024), default='none', nullable=False
    )
    description: str = Column(String(length=1024), nullable=True)


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    description: str = Column(
        String(length=128), nullable=True
    )
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow
    )
    amount: int = Column(Integer, nullable=False)

    user_id = mapped_column(
        Integer, ForeignKey("user.id")
    )
    user = relationship('User')
    tariff_id = mapped_column(
        Integer, ForeignKey("tariff.id")
    )
    outstanding_balance: int = Column(Integer)
