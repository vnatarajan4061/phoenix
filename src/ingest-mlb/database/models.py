"""
SQLAlchemy models for MLB data ingestion.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from common.database.base import Base


class TeamSchedule(Base):
    """MLB team schedule and game information."""

    __tablename__ = "team_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_date: Mapped[str] = mapped_column(String(10), index=True)
    game_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    home_team_id: Mapped[int] = mapped_column(Integer)
    home_team_name: Mapped[str] = mapped_column(String(100))
    away_team_id: Mapped[int] = mapped_column(Integer)
    away_team_name: Mapped[str] = mapped_column(String(100))
