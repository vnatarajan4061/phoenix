"""
Common database configuration utilities.
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Load .env from project root (works from any location)
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)


def get_database_url() -> str:
    """
    Get the database URL from environment variables.

    Supports both local PostgreSQL and Supabase:
    - Local: postgresql+asyncpg://user:password@localhost:5432/mlb_db
    - Supabase: postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def create_async_db_engine(echo: bool = False):
    """
    Create an async SQLAlchemy engine.

    Args:
        echo: If True, SQL queries will be logged (useful for debugging)
    """
    return create_async_engine(
        get_database_url(),
        echo=echo,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Maximum number of connections in the pool
        max_overflow=20,  # Maximum overflow connections
    )


def create_session_maker(engine) -> async_sessionmaker:
    """
    Create an async session maker for the given engine.
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db(session_maker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Usage:
        async for session in get_db(session_maker):
            # use session
    """
    async with session_maker() as session:
        yield session
