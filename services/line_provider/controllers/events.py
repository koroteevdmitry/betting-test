import json
from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import db_session
from models.events import EventState, EventModel
from settings import redis, settings

router = APIRouter(prefix="/events", tags=["events"])


class EventResponse(BaseModel):
    id: UUID
    name: str
    coefficient: float
    deadline: datetime
    state: EventState

    class Config:
        orm_mode = True


class PaginatedEventsResponse(BaseModel):
    limit: int
    offset: int
    total: int
    count: int
    items: List[EventResponse]

    def __init__(self, **data):
        data.setdefault('count', len(data.get('items', [])))
        super().__init__(**data)


class CreateEventRequestPayload(BaseModel):
    name: str = Field(..., example="Liverpool vs Manchester United")
    coefficient: float = Field(..., example=1.2)
    deadline: datetime = Field(..., example="2023-05-01T12:00:00")

    @validator("deadline")
    def deadline_must_be_in_future(cls, v):
        if v < datetime.now():
            raise ValueError("Deadline must be in future.")
        return v


class UpdateEventRequestPayload(BaseModel):
    name: Optional[str] = Field(None, example="Liverpool vs Manchester United")
    coefficient: Optional[float] = Field(None, example=1.2)
    state: Optional[EventState] = Field(None)


@router.get("/", response_model=PaginatedEventsResponse)
async def get_events(
    session: AsyncSession = Depends(db_session),
    limit: int = 10,
    offset: int = 0,
    is_active: bool = False,
):
    query = select(EventModel)
    if is_active:
        query = query.where(and_(EventModel.state == EventState.active, EventModel.deadline > datetime.now()))
    result = await session.execute(query)

    items = result.scalars().all()
    total = (
        await session.execute(select(func.count()).select_from(query.subquery()))
    ).scalar_one() if items else 0

    return PaginatedEventsResponse(
        limit=limit,
        offset=offset,
        total=total,
        items=items,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, session: AsyncSession = Depends(db_session)):
    event = await session.get(EventModel, event_id)
    if not event:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Event not found.")
    return event


@router.post("/", status_code=HTTPStatus.CREATED, response_model=EventResponse)
async def create_event(payload: CreateEventRequestPayload,  session: AsyncSession = Depends(db_session)):
    event = EventModel(state=EventState.active, **payload.dict())
    session.add(event)
    await session.commit()
    return event


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    payload: UpdateEventRequestPayload,
    session: AsyncSession = Depends(db_session),
):
    event = await session.get(EventModel, event_id)
    if not event:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Event not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(event, field, value)
    await session.commit()

    await redis.publish(
        channel=settings.REDIS_CHANNEL,
        message=json.dumps({"event_id": str(event_id), "state": str(event.state.value)})
    )

    return event
