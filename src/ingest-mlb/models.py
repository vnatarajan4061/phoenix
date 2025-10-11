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


class BatterGameLog(CustomModel):
    # Game & Player identifiers
    game_id: int = Field(..., alias="gamePk")
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    opponent_team_id: int = Field(..., alias="opponentTeamId")
    is_home: bool = Field(..., alias="isHome")

    # Position information
    position_code: str | None = Field(default=None, alias="positionCode")
    position_name: str | None = Field(default=None, alias="positionName")
    position_type: str | None = Field(default=None, alias="positionType")

    # Game summary
    batting_summary: str | None = Field(default=None, alias="battingSummary")

    # Core batting stats
    games_played: int = Field(default=0, alias="gamesPlayed")
    at_bats: int = Field(default=0, alias="atBats")
    runs: int = Field(default=0, alias="runs")
    hits: int = Field(default=0, alias="hits")
    doubles: int = Field(default=0, alias="doubles")
    triples: int = Field(default=0, alias="triples")
    home_runs: int = Field(default=0, alias="homeRuns")
    rbi: int = Field(default=0, alias="rbi")
    base_on_balls: int = Field(default=0, alias="baseOnBalls")
    intentional_walks: int = Field(default=0, alias="intentionalWalks")
    strike_outs: int = Field(default=0, alias="strikeOuts")
    stolen_bases: int = Field(default=0, alias="stolenBases")
    caught_stealing: int = Field(default=0, alias="caughtStealing")
    hit_by_pitch: int = Field(default=0, alias="hitByPitch")
    sac_bunts: int = Field(default=0, alias="sacBunts")
    sac_flies: int = Field(default=0, alias="sacFlies")

    # Advanced batting stats
    plate_appearances: int = Field(default=0, alias="plateAppearances")
    total_bases: int = Field(default=0, alias="totalBases")
    left_on_base: int = Field(default=0, alias="leftOnBase")
    ground_into_double_play: int = Field(default=0, alias="groundIntoDoublePlay")
    ground_into_triple_play: int = Field(default=0, alias="groundIntoTriplePlay")
    catchers_interference: int = Field(default=0, alias="catchersInterference")
    pickoffs: int = Field(default=0, alias="pickoffs")

    # Batted ball types
    ground_outs: int = Field(default=0, alias="groundOuts")
    fly_outs: int = Field(default=0, alias="flyOuts")
    air_outs: int = Field(default=0, alias="airOuts")
    pop_outs: int = Field(default=0, alias="popOuts")
    line_outs: int = Field(default=0, alias="lineOuts")

    # Rate stats (for reference, can be calculated downstream)
    stolen_base_percentage: str | None = Field(
        default=None, alias="stolenBasePercentage"
    )
    at_bats_per_home_run: str | None = Field(default=None, alias="atBatsPerHomeRun")

    @model_validator(mode="before")
    @classmethod
    def extract_batter_game_log(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Extract and flatten batting data from boxscore player structure"""

        # Extract position info
        if "position" in values and isinstance(values["position"], dict):
            values["positionCode"] = values["position"].get("code")
            values["positionName"] = values["position"].get("name")
            values["positionType"] = values["position"].get("type")

        # Extract batting stats from stats.batting
        if "stats" in values and "batting" in values["stats"]:
            batting = values["stats"]["batting"]
            values["battingSummary"] = batting.get("summary")
            values["gamesPlayed"] = batting.get("gamesPlayed", 0)
            values["atBats"] = batting.get("atBats", 0)
            values["runs"] = batting.get("runs", 0)
            values["hits"] = batting.get("hits", 0)
            values["doubles"] = batting.get("doubles", 0)
            values["triples"] = batting.get("triples", 0)
            values["homeRuns"] = batting.get("homeRuns", 0)
            values["rbi"] = batting.get("rbi", 0)
            values["baseOnBalls"] = batting.get("baseOnBalls", 0)
            values["intentionalWalks"] = batting.get("intentionalWalks", 0)
            values["strikeOuts"] = batting.get("strikeOuts", 0)
            values["stolenBases"] = batting.get("stolenBases", 0)
            values["caughtStealing"] = batting.get("caughtStealing", 0)
            values["hitByPitch"] = batting.get("hitByPitch", 0)
            values["sacBunts"] = batting.get("sacBunts", 0)
            values["sacFlies"] = batting.get("sacFlies", 0)
            values["plateAppearances"] = batting.get("plateAppearances", 0)
            values["totalBases"] = batting.get("totalBases", 0)
            values["leftOnBase"] = batting.get("leftOnBase", 0)
            values["groundIntoDoublePlay"] = batting.get("groundIntoDoublePlay", 0)
            values["groundIntoTriplePlay"] = batting.get("groundIntoTriplePlay", 0)
            values["catchersInterference"] = batting.get("catchersInterference", 0)
            values["pickoffs"] = batting.get("pickoffs", 0)
            values["groundOuts"] = batting.get("groundOuts", 0)
            values["flyOuts"] = batting.get("flyOuts", 0)
            values["airOuts"] = batting.get("airOuts", 0)
            values["popOuts"] = batting.get("popOuts", 0)
            values["lineOuts"] = batting.get("lineOuts", 0)
            values["stolenBasePercentage"] = batting.get("stolenBasePercentage")
            values["atBatsPerHomeRun"] = batting.get("atBatsPerHomeRun")

        return values


class PitcherGameLog(CustomModel):
    # Game & Player identifiers
    game_id: int = Field(..., alias="gamePk")
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    opponent_team_id: int = Field(..., alias="opponentTeamId")
    is_home: bool = Field(..., alias="isHome")

    # Position information
    position_code: str | None = Field(default=None, alias="positionCode")
    position_name: str | None = Field(default=None, alias="positionName")

    # Game summary
    pitching_summary: str | None = Field(default=None, alias="pitchingSummary")
    pitching_note: str | None = Field(default=None, alias="pitchingNote")

    # Core pitching stats
    games_played: int = Field(default=0, alias="gamesPlayed")
    games_started: int = Field(default=0, alias="gamesStarted")
    games_finished: int = Field(default=0, alias="gamesFinished")
    complete_games: int = Field(default=0, alias="completeGames")
    shutouts: int = Field(default=0, alias="shutouts")
    wins: int = Field(default=0, alias="wins")
    losses: int = Field(default=0, alias="losses")
    saves: int = Field(default=0, alias="saves")
    save_opportunities: int = Field(default=0, alias="saveOpportunities")
    holds: int = Field(default=0, alias="holds")
    blown_saves: int = Field(default=0, alias="blownSaves")

    # Innings and batters
    innings_pitched: str | None = Field(default=None, alias="inningsPitched")
    batters_faced: int = Field(default=0, alias="battersFaced")
    outs: int = Field(default=0, alias="outs")

    # Pitch counts
    pitches_thrown: int = Field(default=0, alias="pitchesThrown")
    strikes: int = Field(default=0, alias="strikes")
    balls: int = Field(default=0, alias="balls")
    strike_percentage: str | None = Field(default=None, alias="strikePercentage")

    # Results allowed
    hits: int = Field(default=0, alias="hits")
    runs: int = Field(default=0, alias="runs")
    earned_runs: int = Field(default=0, alias="earnedRuns")
    home_runs: int = Field(default=0, alias="homeRuns")
    strike_outs: int = Field(default=0, alias="strikeOuts")
    base_on_balls: int = Field(default=0, alias="baseOnBalls")
    intentional_walks: int = Field(default=0, alias="intentionalWalks")
    hit_batsmen: int = Field(default=0, alias="hitBatsmen")

    # Advanced pitching stats
    wild_pitches: int = Field(default=0, alias="wildPitches")
    balks: int = Field(default=0, alias="balks")
    pickoffs: int = Field(default=0, alias="pickoffs")
    inherited_runners: int = Field(default=0, alias="inheritedRunners")
    inherited_runners_scored: int = Field(default=0, alias="inheritedRunnersScored")
    passed_ball: int = Field(default=0, alias="passedBall")

    # Batted ball types allowed
    ground_outs: int = Field(default=0, alias="groundOuts")
    fly_outs: int = Field(default=0, alias="flyOuts")
    air_outs: int = Field(default=0, alias="airOuts")
    pop_outs: int = Field(default=0, alias="popOuts")
    line_outs: int = Field(default=0, alias="lineOuts")
    doubles: int = Field(default=0, alias="doubles")
    triples: int = Field(default=0, alias="triples")

    # Other stats
    rbi: int = Field(default=0, alias="rbi")
    sac_bunts: int = Field(default=0, alias="sacBunts")
    sac_flies: int = Field(default=0, alias="sacFlies")
    catchers_interference: int = Field(default=0, alias="catchersInterference")
    stolen_bases: int = Field(default=0, alias="stolenBases")
    caught_stealing: int = Field(default=0, alias="caughtStealing")
    stolen_base_percentage: str | None = Field(
        default=None, alias="stolenBasePercentage"
    )

    # Rate stats (for reference)
    runs_scored_per_9: str | None = Field(default=None, alias="runsScoredPer9")
    home_runs_per_9: str | None = Field(default=None, alias="homeRunsPer9")

    @model_validator(mode="before")
    @classmethod
    def extract_pitcher_game_log(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Extract and flatten pitching data from boxscore player structure"""

        # Extract position info
        if "position" in values and isinstance(values["position"], dict):
            values["positionCode"] = values["position"].get("code")
            values["positionName"] = values["position"].get("name")

        # Extract pitching stats from stats.pitching
        if "stats" in values and "pitching" in values["stats"]:
            pitching = values["stats"]["pitching"]
            values["pitchingSummary"] = pitching.get("summary")
            values["pitchingNote"] = pitching.get("note")
            values["gamesPlayed"] = pitching.get("gamesPlayed", 0)
            values["gamesStarted"] = pitching.get("gamesStarted", 0)
            values["gamesFinished"] = pitching.get("gamesFinished", 0)
            values["completeGames"] = pitching.get("completeGames", 0)
            values["shutouts"] = pitching.get("shutouts", 0)
            values["wins"] = pitching.get("wins", 0)
            values["losses"] = pitching.get("losses", 0)
            values["saves"] = pitching.get("saves", 0)
            values["saveOpportunities"] = pitching.get("saveOpportunities", 0)
            values["holds"] = pitching.get("holds", 0)
            values["blownSaves"] = pitching.get("blownSaves", 0)
            values["inningsPitched"] = pitching.get("inningsPitched")
            values["battersFaced"] = pitching.get("battersFaced", 0)
            values["outs"] = pitching.get("outs", 0)
            values["pitchesThrown"] = pitching.get("pitchesThrown", 0)
            values["strikes"] = pitching.get("strikes", 0)
            values["balls"] = pitching.get("balls", 0)
            values["strikePercentage"] = pitching.get("strikePercentage")
            values["hits"] = pitching.get("hits", 0)
            values["runs"] = pitching.get("runs", 0)
            values["earnedRuns"] = pitching.get("earnedRuns", 0)
            values["homeRuns"] = pitching.get("homeRuns", 0)
            values["strikeOuts"] = pitching.get("strikeOuts", 0)
            values["baseOnBalls"] = pitching.get("baseOnBalls", 0)
            values["intentionalWalks"] = pitching.get("intentionalWalks", 0)
            values["hitBatsmen"] = pitching.get("hitBatsmen", 0)
            values["wildPitches"] = pitching.get("wildPitches", 0)
            values["balks"] = pitching.get("balks", 0)
            values["pickoffs"] = pitching.get("pickoffs", 0)
            values["inheritedRunners"] = pitching.get("inheritedRunners", 0)
            values["inheritedRunnersScored"] = pitching.get("inheritedRunnersScored", 0)
            values["passedBall"] = pitching.get("passedBall", 0)
            values["groundOuts"] = pitching.get("groundOuts", 0)
            values["flyOuts"] = pitching.get("flyOuts", 0)
            values["airOuts"] = pitching.get("airOuts", 0)
            values["popOuts"] = pitching.get("popOuts", 0)
            values["lineOuts"] = pitching.get("lineOuts", 0)
            values["doubles"] = pitching.get("doubles", 0)
            values["triples"] = pitching.get("triples", 0)
            values["rbi"] = pitching.get("rbi", 0)
            values["sacBunts"] = pitching.get("sacBunts", 0)
            values["sacFlies"] = pitching.get("sacFlies", 0)
            values["catchersInterference"] = pitching.get("catchersInterference", 0)
            values["stolenBases"] = pitching.get("stolenBases", 0)
            values["caughtStealing"] = pitching.get("caughtStealing", 0)
            values["stolenBasePercentage"] = pitching.get("stolenBasePercentage")
            values["runsScoredPer9"] = pitching.get("runsScoredPer9")
            values["homeRunsPer9"] = pitching.get("homeRunsPer9")

        return values
