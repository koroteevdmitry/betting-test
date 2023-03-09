import asyncio
import json

import aioredis
import databases
from fastapi import FastAPI
from fastapi_redis_cache import FastApiRedisCache
from sqlalchemy import update
from starlette.middleware.cors import CORSMiddleware

from controllers.bets import router as bet_router
from models import Bet
from settings import redis, settings

app = FastAPI()
app.include_router(bet_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = databases.Database(settings.DB_DSN)

redis_cache = FastApiRedisCache()
redis_cache.init(
    host_url=settings.REDIS_URL,
    prefix="events-cache",
)


@app.on_event("startup")
async def startup():
    if not db.is_connected:
        await db.connect()


@app.on_event("shutdown")
async def shutdown():
    if db.is_connected:
        await db.disconnect()


# note that this is not a good way to do this, but it's just an example

async def events_reader(channel: aioredis.client.PubSub):
    await pub_sub.subscribe(settings.REDIS_CHANNEL)

    while True:
        try:
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                data = json.loads(message["data"])
                await db.execute(
                    update(Bet).where(Bet.event_uuid == data["event_id"]).values(
                        state=data["state"]
                    )
                )

            await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            pass


pub_sub = redis.pubsub()
asyncio.create_task(events_reader(channel=pub_sub))
