from enum import Enum as EnumBase
from uuid import uuid4

from sqlalchemy import Column, String, Float, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class EventState(str, EnumBase):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


class EventModel(Base):
    __tablename__ = 'events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    coefficient = Column(Float, nullable=False)
    deadline = Column(TIMESTAMP(timezone=True), nullable=False)
    state = Column(Enum(EventState), nullable=False)
