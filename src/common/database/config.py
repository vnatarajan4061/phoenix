import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def create_async_db_engine(echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        get_database_url(),
        echo=echo,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Maximum number of connections in the pool
        max_overflow=20,  # Maximum overflow connections
    )


def create_session_maker(engine) -> async_sessionmaker:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
