from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel


class BetState(str, Enum):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


class Bet(BaseModel):
    id: UUID
    event_uuid: UUID
    amount: float
    state: BetState
    created_at: datetime

    @classmethod
    def create(cls, **data):
        data.setdefault('id', uuid4())
        data.setdefault('created_at', datetime.now().astimezone())
        data.setdefault('state', BetState.active)
        return cls.parse_obj(data)

