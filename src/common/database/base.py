"""
Common database base classes and utilities shared across all services.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models across services."""

    pass
