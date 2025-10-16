"""
MLB-specific database configuration and session management.
"""

from common.database.config import create_async_db_engine, create_session_maker

# Create async engine (set echo=True for SQL query logging during development)
engine = create_async_db_engine(echo=True)

# Create async session factory
AsyncSessionLocal = create_session_maker(engine)
