
from sqlalchemy import Column, String, Float, TIMESTAMP, Enum

from db.base import Base, DefaultColumnsMixin
from schemas.events import EventState


class EventModel(DefaultColumnsMixin, Base):
    __tablename__ = 'events'
    name = Column(String, nullable=False)
    coefficient = Column(Float, nullable=False)
    deadline = Column(TIMESTAMP(timezone=True), nullable=False)
    state = Column(Enum(EventState), nullable=False)
