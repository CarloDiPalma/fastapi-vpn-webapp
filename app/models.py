from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (TIMESTAMP, BigInteger, Boolean, Column, ForeignKey,
                        Integer, String, MetaData, DateTime)
from sqlalchemy.orm import DeclarativeBase, mapped_column

metadata = MetaData()


class Base(DeclarativeBase):
    metadata = metadata


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tg_id: int = Column(BigInteger, unique=True, nullable=False)
    subscription: str = Column(
        String(length=1024), default='none', nullable=False
    )
    username: str = Column(String(length=1024), nullable=False)
    full_name: str = Column(String(length=1024), nullable=False)
    parent_id = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    protocol_id = mapped_column(Integer, ForeignKey("protocol.id"), nullable=True)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_trial: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow)


class Plan(Base):
    __tablename__ = 'plan'

    id = Column(Integer, primary_key=True)
    name: str = Column(
        String(length=1024), default='none', nullable=False
    )
    description: str = Column(String(length=1024), nullable=True)


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
