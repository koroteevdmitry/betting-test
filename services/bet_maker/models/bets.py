from datetime import datetime
from enum import Enum as EnumBase
from uuid import uuid4

from sqlalchemy import Column, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class BetState(str, EnumBase):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


class Bet(Base):
    __tablename__ = 'bets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_uuid = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    state = Column(Enum(BetState), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)
