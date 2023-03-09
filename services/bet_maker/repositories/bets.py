from typing import List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from db.base import db_session
from models import BetModel
from schemas.bets import Bet
from schemas.events import Event
from settings import redis


class BetsRepo:
    def __init__(self, db: Session = Depends(db_session)):
        self.db = db
        self.table = BetModel.get_table()

    async def find_all(self, limit: int, offset: int) -> List[Bet]:
        result = await self.db.execute(self.table.select().limit(limit).offset(offset))
        return [Bet(**dict(row)) for row in result]

    async def find_one(self, bet_uuid: UUID) -> Optional[Bet]:
        result = await self.db.execute(self.table.select().where(self.table.c.id == bet_uuid))
        result = result.first()
        return Bet.parse_obj(result) if result else None

    async def create(self, payload: Bet) -> Bet:
        await self.db.execute(self.table.insert().values(**payload.dict()))
        await self.db.commit()
        return payload

    @staticmethod
    async def get_events() -> List[Event]:
        events_keys = await redis.keys()
        return [Event.parse_raw(await redis.get(key)) for key in events_keys]
