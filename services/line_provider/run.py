from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from controllers.events import router as event_router

app = FastAPI()
app.include_router(event_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)