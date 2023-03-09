from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.orm import Session

from db.base import db_session
from models import EventModel
from schemas.events import Event, EventUpdate
from settings import settings, redis


class EventsRepo:
    def __init__(self, db: Session = Depends(db_session)):
        self.db = db
        self.table = EventModel.get_table()

    async def find_all(self, limit: int, offset: int) -> List[Event]:
        result = await self.db.execute(
            self.table.select().limit(limit).offset(offset))
        return [Event(**dict(row)) for row in result]

    async def find_one(self, event_id: UUID) -> Optional[Event]:
        result = await self.db.execute(self.table.select().where(self.table.c.id == event_id))
        result = result.first()
        return Event.parse_obj(result) if result else None

    async def create(self, payload: Event) -> Event:
        await self.db.execute(self.table.insert().values(**payload.dict()))
        await self.db.commit()

        time_delta = int((payload.deadline - datetime.now()).total_seconds())

        await redis.set(
            name=str(payload.id),
            value=payload.json(exclude={"state"}),
            ex=time_delta,
        )

        return payload

    async def update_and_return(self, uid: UUID, payload: EventUpdate) -> Event:
        await self.db.execute(
            update(self.table).where(self.table.c.id == uid).values(**payload.dict(exclude_none=True))
        )
        await self.db.commit()
        event = await self.db.execute(self.table.select().where(self.table.c.id == uid))
        event = Event(**dict(event.first()))
        if event:
            await redis.publish(
                channel=settings.REDIS_CHANNEL,
                message=event.json(),
            )

        return event
