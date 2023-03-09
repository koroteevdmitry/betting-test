from decimal import Decimal
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator

from repositories.bets import BetsRepo
from schemas.bets import Bet
from schemas.events import Event
from settings import redis

router = APIRouter(prefix="/bets", tags=["bets"])


class CreateBetRequestPayload(BaseModel):
    event_uuid: UUID
    amount: float = Field(..., gt=0)

    @validator('amount')
    def validate_precision(cls, v):
        if Decimal(str(v)).as_tuple().exponent != -2:
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, 'Amount must have 2 decimal places')
        return v


@router.get("/", response_model=List[Bet])
async def get_bets(limit: int = 10, offset: int = 0, repository: BetsRepo = Depends()):
    return await repository.find_all(limit=limit, offset=offset)


@router.get("/events", response_model=list[Event])
async def get_events(repository: BetsRepo = Depends()):
    return await repository.get_events()


@router.get("/{bet_uuid}", response_model=Bet)
async def get_bet(bet_uuid: UUID, repository: BetsRepo = Depends()):
    bet = await repository.find_one(bet_uuid)
    if not bet:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'No such Bet found.')
    return bet


@router.post("/", status_code=HTTPStatus.CREATED, response_model=Bet)
async def create_bet(payload: CreateBetRequestPayload, repository: BetsRepo = Depends()):
    if not await redis.exists(str(payload.event_uuid)):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, 'No such Event found.')
    return await repository.create(Bet.create(**payload.dict()))
