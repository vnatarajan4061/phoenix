from typing import Any

from pydantic import Field, model_validator

from common.models import CustomModel


class TeamSchedules(CustomModel):
    game_date: str = Field(..., alias="game_date")
    game_id: int = Field(...)

    @model_validator(mode="before")
    @classmethod
    def parse_games(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["game_id"] = values["game_pk"]
        return values
