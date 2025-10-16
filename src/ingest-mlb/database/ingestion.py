from typing import List

from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.config import AsyncSessionLocal
from database.models import TeamSchedule


async def ingest_schedules(schedules: List) -> int:
    """
    Ingest MLB team schedules into the database.

    Uses PostgreSQL's ON CONFLICT to upsert records.

    Args:
        schedules: List of validated Pydantic TeamSchedules objects
                   (already validated by mlb.process_schedules)

    Returns:
        Number of schedules processed
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Convert Pydantic models to dicts for bulk insert
            # The schedules are already validated Pydantic models from mlb.py
            schedule_dicts = [
                {
                    "game_date": s.game_date,
                    "game_id": s.game_id,
                    "home_team_id": s.home_team_id,
                    "home_team_name": s.home_team_name,
                    "away_team_id": s.away_team_id,
                    "away_team_name": s.away_team_name,
                }
                for s in schedules
            ]

            # Upsert: Insert or update on conflict (duplicate game_id)
            stmt = pg_insert(TeamSchedule).values(schedule_dicts)
            stmt = stmt.on_conflict_do_update(
                index_elements=["game_id"],
                set_={
                    "game_date": stmt.excluded.game_date,
                    "home_team_name": stmt.excluded.home_team_name,
                    "away_team_name": stmt.excluded.away_team_name,
                },
            )

            await session.execute(stmt)
            await session.commit()

    return len(schedules)
