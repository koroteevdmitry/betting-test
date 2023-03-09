from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator

from repositories.events import EventsRepo
from schemas.events import Event, EventState, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


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


@router.get("/", response_model=List[Event])
async def get_events(limit: int = 10, offset: int = 0, repository: EventsRepo = Depends()):
    return await repository.find_all(limit=limit, offset=offset)


@router.post("/", status_code=HTTPStatus.CREATED, response_model=Event)
async def create_event(payload: CreateEventRequestPayload, repository: EventsRepo = Depends()):
    return await repository.create(Event.create(**payload.dict()))


@router.patch("/{event_id}", response_model=Event)
async def update_event(event_id: UUID, payload: UpdateEventRequestPayload, repository: EventsRepo = Depends()):
    if not payload.dict(exclude_unset=True):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, detail='Empty payload.')
    if not await repository.find_one(event_id):
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='No such Event found.')
    return await repository.update_and_return(event_id, EventUpdate.create(**payload.dict()))
