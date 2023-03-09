from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class EventState(str, Enum):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


class Event(BaseModel):
    id: UUID
    name: str
    coefficient: float
    deadline: datetime
    state: EventState

    @classmethod
    def create(cls, **data):
        data.setdefault('id', uuid4())
        data.setdefault('state', EventState.active)
        return cls.parse_obj(data)


class EventUpdate(BaseModel):
    name: Optional[str]
    coefficient: Optional[float]
    state: Optional[EventState]

    @classmethod
    def create(cls, **data):
        return cls.parse_obj(data)