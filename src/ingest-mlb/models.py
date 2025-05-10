from pydantic import Field

from common.models import CustomModel


class TeamSchedules(CustomModel):
    game_date: str = Field(..., alias="game_date")
    game_id: int = Field(..., alias="game_id")
    home_team_id: int = Field(..., alias="home_team_id")
    home_team_name: str = Field(..., alias="home_team_name")
    away_team_id: int = Field(..., alias="away_team_id")
    away_team_name: str = Field(..., alias="away_team_name")
