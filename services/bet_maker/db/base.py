from typing import List, AsyncGenerator

from abc import abstractmethod
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Table
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

SQLALCHEMY_DATABASE_URL = settings.DB_DSN

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative()
class Base:
    @classmethod
    @abstractmethod  # unfortunately, using metaclass=ABCMeta leads to conflicts, so this only for IDE autocompletion
    def get_primary_key(cls) -> List[str]:
        ...

    @classmethod
    def get_table(cls) -> Table:
        return cls.metadata.tables[cls.__tablename__]


@declarative_mixin
class DefaultColumnsMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    @classmethod
    def get_primary_key(cls) -> List[str]:
        return ['id']


async_engine = create_async_engine(settings.DB_DSN, future=True)


async def db_session() -> AsyncGenerator:
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session