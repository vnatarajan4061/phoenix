from datetime import datetime
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


# Core Entity Models for MLB Beat the Streak & ML
class Team(CustomModel):
    team_id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")
    abbreviation: str | None = Field(default=None, alias="abbreviation")
    team_name: str | None = Field(default=None, alias="teamName")
    location_name: str | None = Field(default=None, alias="locationName")
    first_year_of_play: str | None = Field(default=None, alias="firstYearOfPlay")
    league_id: int | None = Field(default=None, alias="league")
    division_id: int | None = Field(default=None, alias="division")
    venue_id: int | None = Field(default=None, alias="venue")

    @model_validator(mode="before")
    @classmethod
    def extract_nested_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["league"] = values["league"]["id"]
        values["division"] = values["division"]["id"]
        values["venue"] = values["venue"]["id"]
        return values


class Player(CustomModel):
    player_id: int = Field(..., alias="id")
    full_name: str = Field(..., alias="fullName")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    birth_date: str | None = Field(default=None, alias="birthDate")
    current_age: int | None = Field(default=None, alias="currentAge")
    birth_city: str | None = Field(default=None, alias="birthCity")
    birth_country: str | None = Field(default=None, alias="birthCountry")
    height: float | None = Field(default=None, alias="height")  # in meters
    weight: int | None = Field(default=None, alias="weight")
    active: bool = Field(default=True, alias="active")
    bat_side_code: str | None = Field(default=None, alias="batSide")
    pitch_hand_code: str | None = Field(default=None, alias="pitchHand")

    @model_validator(mode="before")
    @classmethod
    def parse_height(cls, values: dict[str, Any]) -> dict[str, Any]:
        if (
            "height" in values
            and values["height"]
            and isinstance(values["height"], str)
        ):
            parts = values["height"].replace('"', "").replace("'", " ").split()
            feet = int(parts[0])
            inches = int(parts[1])
            # Convert to total inches, then to meters (1 inch = 0.0254 meters)
            total_inches = (feet * 12) + inches
            values["height"] = round(total_inches * 0.0254, 2)
        return values

    @model_validator(mode="before")
    @classmethod
    def extract_nested_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "batSide" in values and isinstance(values["batSide"], dict):
            values["batSide"] = values["batSide"]["code"]
        if "pitchHand" in values and isinstance(values["pitchHand"], dict):
            values["pitchHand"] = values["pitchHand"]["code"]
        return values


class PlayerTeamHistory(CustomModel):
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    primary_number: int | None = Field(default=None, alias="primaryNumber")
    primary_position_code: str | None = Field(default=None, alias="primaryPosition")
    start_date: datetime = Field(..., alias="startDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    is_current: bool = Field(default=True, alias="isCurrent")

    @model_validator(mode="before")
    @classmethod
    def extract_nested_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "primaryPosition" in values and isinstance(values["primaryPosition"], dict):
            values["primaryPosition"] = values["primaryPosition"]["code"]

        # Set is_current based on end_date
        if values.get("endDate") is None:
            values["isCurrent"] = True
        else:
            values["isCurrent"] = False

        return values
