from pathlib import Path

import aioredis
from pydantic import BaseSettings, PostgresDsn, RedisDsn

BASE_DIR = Path(__file__).parent.resolve()


class Settings(BaseSettings):
    DB_DSN: PostgresDsn
    MIGRATION_DB_DSN: PostgresDsn
    REDIS_URL: RedisDsn
    REDIS_CHANNEL: str = "events"

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()

redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8")
