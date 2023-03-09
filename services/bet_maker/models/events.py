from datetime import datetime
from enum import Enum
from uuid import UUID

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
