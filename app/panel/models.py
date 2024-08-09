from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (TIMESTAMP, BigInteger, Boolean, Column, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Client(Base):
    """Table represent clients objects in panel."""

    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    uuid: str = Column(
        UUID(as_uuid=True), nullable=False
    )
    email: str = Column(
        String(length=50), default='none', nullable=False
    )
    user_id = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    user = relationship('User')
    server_id = mapped_column(
        Integer, ForeignKey("server.id"), nullable=True
    )
    server = relationship('Server')
    is_enabled: bool = Column(Boolean, default=True, nullable=False)
    paid_until = Column(
        TIMESTAMP(timezone=False), nullable=True
    )
