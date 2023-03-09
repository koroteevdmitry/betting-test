from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from typing import List
from uuid import UUID

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_redis_cache import cache_one_minute
from pydantic import BaseModel, Field, validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import db_session
from models import BetState, Bet
from models.events import Event, EventState
from settings import settings

router = APIRouter(prefix="/bets", tags=["bets"])


class PaginatedEventsResponse(BaseModel):
    limit: int
    offset: int
    total: int
    count: int
    items: List[Event]


class BetResponse(BaseModel):
    id: UUID
    event_uuid: UUID
    amount: float
    state: BetState
    created_at: datetime

    class Config:
        orm_mode = True


class CreateBetRequestPayload(BaseModel):
    event_uuid: UUID
    amount: float = Field(..., gt=0)

    # created_at: datetime = Field(default_factory=datetime.now, exclude=True)

    @validator('amount')
    def validate_precision(cls, v):
        if Decimal(str(v)).as_tuple().exponent != -2:
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, 'Amount must have 2 decimal places.')
        return v


@router.get("/events", response_model=PaginatedEventsResponse)
@cache_one_minute()
async def get_events(request: Request, response: Response, limit: int = 10, offset: int = 0):
    async with ClientSession() as client:
        async with client.get(
                f'{settings.EVENTS_API_URL}/events',
                params={'limit': limit, 'offset': offset, 'is_active': True},
        ) as resp:
            if resp.status != HTTPStatus.OK:
                raise HTTPException(resp.status, 'Failed to get Events.')
            return await resp.json()


@router.get("", response_model=List[BetResponse])
async def get_bets(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(db_session)):
    result = await session.execute(select(Bet).limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/{bet_uuid}", response_model=BetResponse)
async def get_bet(bet_uuid: UUID, session: AsyncSession = Depends(db_session)):
    result = await session.execute(select(Bet).where(Bet.id == bet_uuid))
    bet = result.scalars().first()
    if not bet:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'No such Bet found.')
    return BetResponse.from_orm(bet)


@router.post("", status_code=HTTPStatus.CREATED, response_model=BetResponse)
async def create_bet(payload: CreateBetRequestPayload, session: AsyncSession = Depends(db_session)):
    async with ClientSession() as client:
        async with client.get(f'{settings.EVENTS_API_URL}/events/{payload.event_uuid}') as resp:
            if resp.status != HTTPStatus.OK:
                raise HTTPException(resp.status, 'Failed to get Event.')
            event = await resp.json()
            if event['state'] != EventState.active:
                raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, 'Event is not open for betting.')
            if event['deadline'] < datetime.now().isoformat():
                raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, 'Event deadline has passed.')

    bet = Bet(state=BetState.active, **payload.dict())
    session.add(bet)
    await session.commit()
    return BetResponse.from_orm(bet)
