import asyncio
import json

import aioredis
import databases
from fastapi import FastAPI

from models import BetModel
from routers.bet_router import router as bet_router
from settings import redis, settings

app = FastAPI()
app.include_router(bet_router)


db = databases.Database(settings.DB_DSN)


@app.on_event("startup")
async def startup():
    if not db.is_connected:
        await db.connect()


@app.on_event("shutdown")
async def shutdown():
    if db.is_connected:
        await db.disconnect()


async def events_reader(channel: aioredis.client.PubSub):
    await pub_sub.subscribe(settings.REDIS_CHANNEL)

    while True:
        try:
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                data = json.loads(message["data"])
                await db.execute(
                    BetModel.get_table().update(
                        BetModel.get_table().c.event_uuid == data["id"]
                    ).values(state=data["state"])
                )
            await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            pass

pub_sub = redis.pubsub()
asyncio.create_task(events_reader(channel=pub_sub))