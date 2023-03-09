from sqlalchemy import Column, Float, func, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base, DefaultColumnsMixin
from schemas.bets import BetState


class BetModel(DefaultColumnsMixin, Base):
    __tablename__ = 'bets'

    event_uuid = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    state = Column(Enum(BetState), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
