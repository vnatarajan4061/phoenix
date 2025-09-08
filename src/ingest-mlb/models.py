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
    abbreviation: str = Field(..., alias="abbreviation")
    team_name: str = Field(..., alias="teamName")
    location_name: str = Field(..., alias="locationName")
    first_year_of_play: str = Field(..., alias="firstYearOfPlay")
    league_id: int = Field(..., alias="league", description="Extracted from league.id")
    division_id: int = Field(
        ..., alias="division", description="Extracted from division.id"
    )
    venue_id: int = Field(..., alias="venue", description="Extracted from venue.id")

    @model_validator(mode="before")
    @classmethod
    def extract_nested_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "league" in values and isinstance(values["league"], dict):
            values["league"] = values["league"]["id"]
        if "division" in values and isinstance(values["division"], dict):
            values["division"] = values["division"]["id"]
        if "venue" in values and isinstance(values["venue"], dict):
            values["venue"] = values["venue"]["id"]
        return values


class Player(CustomModel):
    player_id: int = Field(..., alias="id")
    full_name: str = Field(..., alias="fullName")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    primary_number: int | None = Field(default=None, alias="primaryNumber")
    birth_date: str | None = Field(default=None, alias="birthDate")
    current_age: int | None = Field(default=None, alias="currentAge")
    birth_city: str | None = Field(default=None, alias="birthCity")
    birth_country: str | None = Field(default=None, alias="birthCountry")
    height: str | None = Field(default=None, alias="height")
    weight: int | None = Field(default=None, alias="weight")
    active: bool = Field(default=True, alias="active")
    primary_position_code: str | None = Field(default=None, alias="primaryPosition")
    bat_side_code: str | None = Field(default=None, alias="batSide")
    pitch_hand_code: str | None = Field(default=None, alias="pitchHand")
    current_team_id: int | None = Field(default=None, alias="currentTeam")

    @model_validator(mode="before")
    @classmethod
    def extract_nested_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "primaryPosition" in values and isinstance(values["primaryPosition"], dict):
            values["primaryPosition"] = values["primaryPosition"]["code"]
        if "batSide" in values and isinstance(values["batSide"], dict):
            values["batSide"] = values["batSide"]["code"]
        if "pitchHand" in values and isinstance(values["pitchHand"], dict):
            values["pitchHand"] = values["pitchHand"]["code"]
        if "currentTeam" in values and isinstance(values["currentTeam"], dict):
            values["currentTeam"] = values["currentTeam"]["id"]
        return values


class PlayerSeasonStats(CustomModel):
    player_id: int = Field(..., alias="person")
    season: int = Field(..., alias="season")
    team_id: int = Field(..., alias="team")
    # Batting stats
    games_played: int = Field(default=0, alias="gamesPlayed")
    ground_outs: int = Field(default=0, alias="groundOuts")
    air_outs: int = Field(default=0, alias="airOuts")
    runs: int = Field(default=0, alias="runs")
    doubles: int = Field(default=0, alias="doubles")
    triples: int = Field(default=0, alias="triples")
    home_runs: int = Field(default=0, alias="homeRuns")
    strike_outs: int = Field(default=0, alias="strikeOuts")
    base_on_balls: int = Field(default=0, alias="baseOnBalls")
    intentional_walks: int = Field(default=0, alias="intentionalWalks")
    hits: int = Field(default=0, alias="hits")
    hit_by_pitch: int = Field(default=0, alias="hitByPitch")
    avg: str = Field(default="0.000", alias="avg")
    at_bats: int = Field(default=0, alias="atBats")
    obp: str = Field(default="0.000", alias="obp")
    slg: str = Field(default="0.000", alias="slg")
    ops: str = Field(default="0.000", alias="ops")
    caught_stealing: int = Field(default=0, alias="caughtStealing")
    stolen_bases: int = Field(default=0, alias="stolenBases")
    plate_appearances: int = Field(default=0, alias="plateAppearances")
    total_bases: int = Field(default=0, alias="totalBases")
    rbi: int = Field(default=0, alias="rbi")
    left_on_base: int = Field(default=0, alias="leftOnBase")
    sac_bunts: int = Field(default=0, alias="sacBunts")
    sac_flies: int = Field(default=0, alias="sacFlies")
    babip: str = Field(default="0.000", alias="babip")

    @model_validator(mode="before")
    @classmethod
    def extract_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "person" in values and isinstance(values["person"], dict):
            values["person"] = values["person"]["id"]
        if "team" in values and isinstance(values["team"], dict):
            values["team"] = values["team"]["id"]
        return values


class BatterVsPitcher(CustomModel):
    batter_id: int = Field(..., alias="batter")
    pitcher_id: int = Field(..., alias="pitcher")
    season: int | None = Field(default=None, alias="season")  # None for career stats
    at_bats: int = Field(default=0, alias="atBats")
    hits: int = Field(default=0, alias="hits")
    doubles: int = Field(default=0, alias="doubles")
    triples: int = Field(default=0, alias="triples")
    home_runs: int = Field(default=0, alias="homeRuns")
    rbi: int = Field(default=0, alias="rbi")
    walks: int = Field(default=0, alias="baseOnBalls")
    strike_outs: int = Field(default=0, alias="strikeOuts")
    avg: str = Field(default="0.000", alias="avg")
    obp: str = Field(default="0.000", alias="obp")
    slg: str = Field(default="0.000", alias="slg")
    ops: str = Field(default="0.000", alias="ops")

    @model_validator(mode="before")
    @classmethod
    def extract_player_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "batter" in values and isinstance(values["batter"], dict):
            values["batter"] = values["batter"]["id"]
        if "pitcher" in values and isinstance(values["pitcher"], dict):
            values["pitcher"] = values["pitcher"]["id"]
        return values


class BatterVsTeam(CustomModel):
    batter_id: int = Field(..., alias="batter")
    opposing_team_id: int = Field(..., alias="team")
    season: int | None = Field(default=None, alias="season")
    at_bats: int = Field(default=0, alias="atBats")
    hits: int = Field(default=0, alias="hits")
    doubles: int = Field(default=0, alias="doubles")
    triples: int = Field(default=0, alias="triples")
    home_runs: int = Field(default=0, alias="homeRuns")
    rbi: int = Field(default=0, alias="rbi")
    walks: int = Field(default=0, alias="baseOnBalls")
    strike_outs: int = Field(default=0, alias="strikeOuts")
    avg: str = Field(default="0.000", alias="avg")
    obp: str = Field(default="0.000", alias="obp")
    slg: str = Field(default="0.000", alias="slg")
    ops: str = Field(default="0.000", alias="ops")

    @model_validator(mode="before")
    @classmethod
    def extract_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "batter" in values and isinstance(values["batter"], dict):
            values["batter"] = values["batter"]["id"]
        if "team" in values and isinstance(values["team"], dict):
            values["team"] = values["team"]["id"]
        return values


class RecentPerformance(CustomModel):
    player_id: int = Field(..., alias="playerId")
    game_date: str = Field(..., alias="gameDate")
    last_5_games_avg: float = Field(default=0.000, alias="last5Avg")
    last_10_games_avg: float = Field(default=0.000, alias="last10Avg")
    last_15_games_avg: float = Field(default=0.000, alias="last15Avg")
    current_hitting_streak: int = Field(default=0, alias="hittingStreak")
    current_on_base_streak: int = Field(default=0, alias="onBaseStreak")
    games_with_hit_last_10: int = Field(default=0, alias="hitsLast10")
    is_hot_streak: bool = Field(default=False, alias="isHot")  # .300+ last 10 games
    is_cold_streak: bool = Field(default=False, alias="isCold")  # .200- last 10 games


class AtBat(CustomModel):
    game_id: int = Field(..., alias="gamePk")
    at_bat_index: int = Field(..., alias="atBatIndex")
    batter_id: int = Field(..., alias="batter")
    pitcher_id: int = Field(..., alias="pitcher")
    inning: int = Field(..., alias="inning")
    inning_half: str = Field(..., alias="halfInning")  # "top" or "bottom"
    outs: int = Field(..., alias="outs")
    balls: int = Field(..., alias="balls")
    strikes: int = Field(..., alias="strikes")
    result: str = Field(..., alias="result")  # "Hit", "Strikeout", "Walk", etc.
    result_type: str = Field(..., alias="type")  # "atBat", "action", etc.
    rbi: int = Field(default=0, alias="rbi")
    runners_on_base: int = Field(default=0, alias="runnersOnBase")

    @model_validator(mode="before")
    @classmethod
    def extract_at_bat_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "batter" in values and isinstance(values["batter"], dict):
            values["batter"] = values["batter"]["id"]
        if "pitcher" in values and isinstance(values["pitcher"], dict):
            values["pitcher"] = values["pitcher"]["id"]
        if "result" in values and isinstance(values["result"], dict):
            values["result"] = values["result"]["description"]
            values["type"] = values["result"]["type"]
            values["rbi"] = values["result"].get("rbi", 0)
        return values
