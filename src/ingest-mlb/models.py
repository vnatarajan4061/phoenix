from typing import Any

from pydantic import Field, model_validator

from common.models import CustomModel


class TeamSchedules(CustomModel):
    game_date: str = Field(..., alias="game_date")
    game_id: int = Field(..., alias="game_id")
    home_team_id: int = Field(..., alias="home_team_id")
    home_team_name: str = Field(..., alias="home_team_name")
    away_team_id: int = Field(..., alias="away_team_id")
    away_team_name: str = Field(..., alias="away_team_name")

    @model_validator(mode="before")
    @classmethod
    def process_team_id_names(cls, values: dict[str, Any]) -> dict[str, Any]:
        for team in ["home", "away"]:
            values[f"{team}_team_id"] = values["teams"][team]["team"]["id"]
            values[f"{team}_team_name"] = values["teams"][team]["team"]["name"]

        return values


class GameInformation(CustomModel):
    game_id: int = Field(..., alias="game_id")
    wind: str | None = Field(default=None)
    temperature: int | None = Field(default=None)
    weather_condition: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def process_game_weather(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["wind"] = values["weather"].get("wind")
        values["temperature"] = values["weather"].get("temp")
        values["weather_condition"] = values["weather"].get("condition")

        return values

    # @model_validator(mode="before")
    # @classmethod
    # def process_game_boxscore(cls, values: dict[str, Any]) -> dict[str, Any]:
    #     return values
