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
    game_date: str = Field(...)
    game_datetime: str | None = Field(default=None)
    game_status: str | None = Field(default=None)
    detailed_state: str | None = Field(default=None)
    day_night: str | None = Field(default=None)
    venue_id: int | None = Field(default=None)
    venue_name: str | None = Field(default=None)
    home_team_id: int | None = Field(default=None)
    home_team_name: str | None = Field(default=None)
    away_team_id: int | None = Field(default=None)
    away_team_name: str | None = Field(default=None)
    home_wins: int | None = Field(default=None)
    home_losses: int | None = Field(default=None)
    home_win_pct: str | None = Field(default=None)
    away_wins: int | None = Field(default=None)
    away_losses: int | None = Field(default=None)
    away_win_pct: str | None = Field(default=None)
    home_score: int | None = Field(default=None)
    away_score: int | None = Field(default=None)
    wind: str | None = Field(default=None)
    temperature: int | None = Field(default=None)
    weather_condition: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def process_game_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        datetime_info = values["datetime"]
        status_info = values["status"]
        venue_info = values["venue"]
        teams_info = values["teams"]
        home_team = teams_info.get("home", {})
        away_team = teams_info.get("away", {})
        home_record = home_team.get("record", {})
        away_record = away_team.get("record", {})
        linescore_teams = values["linescore"].get("teams", {})
        weather_info = values["weather"]

        # Date/time from datetime dict
        values["game_date"] = datetime_info.get("officialDate")
        values["game_datetime"] = datetime_info.get("dateTime")
        values["day_night"] = datetime_info.get("dayNight")

        # Status from status dict
        values["game_status"] = status_info.get("abstractGameState")
        values["detailed_state"] = status_info.get("detailedState")

        # Venue from venue dict
        values["venue_id"] = venue_info.get("id")
        values["venue_name"] = venue_info.get("name")

        # Home team from teams dict
        values["home_team_id"] = home_team.get("id")
        values["home_team_name"] = home_team.get("name")
        values["home_wins"] = home_record.get("wins")
        values["home_losses"] = home_record.get("losses")
        values["home_win_pct"] = home_record.get("winningPercentage")

        # Away team from teams dict
        values["away_team_id"] = away_team.get("id")
        values["away_team_name"] = away_team.get("name")
        values["away_wins"] = away_record.get("wins")
        values["away_losses"] = away_record.get("losses")
        values["away_win_pct"] = away_record.get("winningPercentage")

        # Scores from linescore dict
        values["home_score"] = linescore_teams.get("home", {}).get("runs")
        values["away_score"] = linescore_teams.get("away", {}).get("runs")

        # Weather from weather dict
        values["wind"] = weather_info.get("wind")
        values["temperature"] = weather_info.get("temp")
        values["weather_condition"] = weather_info.get("condition")

        return values


class Team(CustomModel):
    team_id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")
    abbreviation: str | None = Field(default=None, alias="abbreviation")
    team_name: str | None = Field(default=None, alias="teamName")
    location_name: str | None = Field(default=None, alias="locationName")
    first_year_of_play: str | None = Field(default=None, alias="firstYearOfPlay")
    league_id: int | None = Field(default=None)
    division_id: int | None = Field(default=None)
    venue_id: int | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["league_id"] = values["league"]["id"]
        values["division_id"] = values["division"]["id"]
        values["venue_id"] = values["venue"]["id"]
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
    bat_side_code: str | None = Field(default=None)
    pitch_hand_code: str | None = Field(default=None)

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
            values["bat_side_code"] = values["batSide"]["code"]
        if "pitchHand" in values and isinstance(values["pitchHand"], dict):
            values["pitch_hand_code"] = values["pitchHand"]["code"]
        return values


class PlayerTeamHistory(CustomModel):
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    primary_number: int | None = Field(default=None, alias="primaryNumber")
    primary_position_code: str | None = Field(default=None)
    start_date: datetime = Field(..., alias="startDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    is_current: bool = Field(default=True)

    @model_validator(mode="before")
    @classmethod
    def extract_nested_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "primaryPosition" in values and isinstance(values["primaryPosition"], dict):
            values["primary_position_code"] = values["primaryPosition"]["code"]

        # Set is_current based on end_date
        if values.get("endDate") is None:
            values["is_current"] = True
        else:
            values["is_current"] = False

        return values


class BatterGameLog(CustomModel):
    game_id: int = Field(..., alias="gamePk")
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    opponent_team_id: int = Field(..., alias="opponentTeamId")
    is_home: bool = Field(..., alias="isHome")
    position_code: str | None = Field(default=None)
    position_name: str | None = Field(default=None)
    position_type: str | None = Field(default=None)
    batting_summary: str | None = Field(default=None)
    games_played: int = Field(default=0)
    at_bats: int = Field(default=0)
    runs: int = Field(default=0)
    hits: int = Field(default=0)
    doubles: int = Field(default=0)
    triples: int = Field(default=0)
    home_runs: int = Field(default=0)
    rbi: int = Field(default=0)
    base_on_balls: int = Field(default=0)
    intentional_walks: int = Field(default=0)
    strike_outs: int = Field(default=0)
    stolen_bases: int = Field(default=0)
    caught_stealing: int = Field(default=0)
    hit_by_pitch: int = Field(default=0)
    sac_bunts: int = Field(default=0)
    sac_flies: int = Field(default=0)
    plate_appearances: int = Field(default=0)
    total_bases: int = Field(default=0)
    left_on_base: int = Field(default=0)
    ground_into_double_play: int = Field(default=0)
    ground_into_triple_play: int = Field(default=0)
    catchers_interference: int = Field(default=0)
    pickoffs: int = Field(default=0)
    ground_outs: int = Field(default=0)
    fly_outs: int = Field(default=0)
    air_outs: int = Field(default=0)
    pop_outs: int = Field(default=0)
    line_outs: int = Field(default=0)
    stolen_base_percentage: str | None = Field(default=None)
    at_bats_per_home_run: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def extract_batter_game_log(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Extract position info
        if "position" in values and isinstance(values["position"], dict):
            values["position_code"] = values["position"].get("code")
            values["position_name"] = values["position"].get("name")
            values["position_type"] = values["position"].get("type")

        # Extract batting stats from stats.batting
        if "stats" in values and "batting" in values["stats"]:
            batting = values["stats"]["batting"]
            values["batting_summary"] = batting.get("summary")
            values["games_played"] = batting.get("gamesPlayed", 0)
            values["at_bats"] = batting.get("atBats", 0)
            values["runs"] = batting.get("runs", 0)
            values["hits"] = batting.get("hits", 0)
            values["doubles"] = batting.get("doubles", 0)
            values["triples"] = batting.get("triples", 0)
            values["home_runs"] = batting.get("homeRuns", 0)
            values["rbi"] = batting.get("rbi", 0)
            values["base_on_balls"] = batting.get("baseOnBalls", 0)
            values["intentional_walks"] = batting.get("intentionalWalks", 0)
            values["strike_outs"] = batting.get("strikeOuts", 0)
            values["stolen_bases"] = batting.get("stolenBases", 0)
            values["caught_stealing"] = batting.get("caughtStealing", 0)
            values["hit_by_pitch"] = batting.get("hitByPitch", 0)
            values["sac_bunts"] = batting.get("sacBunts", 0)
            values["sac_flies"] = batting.get("sacFlies", 0)
            values["plate_appearances"] = batting.get("plateAppearances", 0)
            values["total_bases"] = batting.get("totalBases", 0)
            values["left_on_base"] = batting.get("leftOnBase", 0)
            values["ground_into_double_play"] = batting.get("groundIntoDoublePlay", 0)
            values["ground_into_triple_play"] = batting.get("groundIntoTriplePlay", 0)
            values["catchers_interference"] = batting.get("catchersInterference", 0)
            values["pickoffs"] = batting.get("pickoffs", 0)
            values["ground_outs"] = batting.get("groundOuts", 0)
            values["fly_outs"] = batting.get("flyOuts", 0)
            values["air_outs"] = batting.get("airOuts", 0)
            values["pop_outs"] = batting.get("popOuts", 0)
            values["line_outs"] = batting.get("lineOuts", 0)
            values["stolen_base_percentage"] = batting.get("stolenBasePercentage")
            values["at_bats_per_home_run"] = batting.get("atBatsPerHomeRun")

        return values


class PitcherGameLog(CustomModel):
    game_id: int = Field(..., alias="gamePk")
    player_id: int = Field(..., alias="playerId")
    team_id: int = Field(..., alias="teamId")
    opponent_team_id: int = Field(..., alias="opponentTeamId")
    is_home: bool = Field(..., alias="isHome")
    position_code: str | None = Field(default=None)
    position_name: str | None = Field(default=None)
    pitching_summary: str | None = Field(default=None)
    pitching_note: str | None = Field(default=None)
    games_played: int = Field(default=0)
    games_started: int = Field(default=0)
    games_finished: int = Field(default=0)
    complete_games: int = Field(default=0)
    shutouts: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    saves: int = Field(default=0)
    save_opportunities: int = Field(default=0)
    holds: int = Field(default=0)
    blown_saves: int = Field(default=0)
    innings_pitched: str | None = Field(default=None)
    batters_faced: int = Field(default=0)
    outs: int = Field(default=0)
    pitches_thrown: int = Field(default=0)
    strikes: int = Field(default=0)
    balls: int = Field(default=0)
    strike_percentage: str | None = Field(default=None)
    hits: int = Field(default=0)
    runs: int = Field(default=0)
    earned_runs: int = Field(default=0)
    home_runs: int = Field(default=0)
    strike_outs: int = Field(default=0)
    base_on_balls: int = Field(default=0)
    intentional_walks: int = Field(default=0)
    hit_batsmen: int = Field(default=0)
    wild_pitches: int = Field(default=0)
    balks: int = Field(default=0)
    pickoffs: int = Field(default=0)
    inherited_runners: int = Field(default=0)
    inherited_runners_scored: int = Field(default=0)
    passed_ball: int = Field(default=0)
    ground_outs: int = Field(default=0)
    fly_outs: int = Field(default=0)
    air_outs: int = Field(default=0)
    pop_outs: int = Field(default=0)
    line_outs: int = Field(default=0)
    doubles: int = Field(default=0)
    triples: int = Field(default=0)
    rbi: int = Field(default=0)
    sac_bunts: int = Field(default=0)
    sac_flies: int = Field(default=0)
    catchers_interference: int = Field(default=0)
    stolen_bases: int = Field(default=0)
    caught_stealing: int = Field(default=0)
    stolen_base_percentage: str | None = Field(default=None)
    runs_scored_per_9: str | None = Field(default=None)
    home_runs_per_9: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def extract_pitcher_game_log(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Extract position info
        if "position" in values and isinstance(values["position"], dict):
            values["position_code"] = values["position"].get("code")
            values["position_name"] = values["position"].get("name")

        # Extract pitching stats from stats.pitching
        if "stats" in values and "pitching" in values["stats"]:
            pitching = values["stats"]["pitching"]
            values["pitching_summary"] = pitching.get("summary")
            values["pitching_note"] = pitching.get("note")
            values["games_played"] = pitching.get("gamesPlayed", 0)
            values["games_started"] = pitching.get("gamesStarted", 0)
            values["games_finished"] = pitching.get("gamesFinished", 0)
            values["complete_games"] = pitching.get("completeGames", 0)
            values["shutouts"] = pitching.get("shutouts", 0)
            values["wins"] = pitching.get("wins", 0)
            values["losses"] = pitching.get("losses", 0)
            values["saves"] = pitching.get("saves", 0)
            values["save_opportunities"] = pitching.get("saveOpportunities", 0)
            values["holds"] = pitching.get("holds", 0)
            values["blown_saves"] = pitching.get("blownSaves", 0)
            values["innings_pitched"] = pitching.get("inningsPitched")
            values["batters_faced"] = pitching.get("battersFaced", 0)
            values["outs"] = pitching.get("outs", 0)
            values["pitches_thrown"] = pitching.get("pitchesThrown", 0)
            values["strikes"] = pitching.get("strikes", 0)
            values["balls"] = pitching.get("balls", 0)
            values["strike_percentage"] = pitching.get("strikePercentage")
            values["hits"] = pitching.get("hits", 0)
            values["runs"] = pitching.get("runs", 0)
            values["earned_runs"] = pitching.get("earnedRuns", 0)
            values["home_runs"] = pitching.get("homeRuns", 0)
            values["strike_outs"] = pitching.get("strikeOuts", 0)
            values["base_on_balls"] = pitching.get("baseOnBalls", 0)
            values["intentional_walks"] = pitching.get("intentionalWalks", 0)
            values["hit_batsmen"] = pitching.get("hitBatsmen", 0)
            values["wild_pitches"] = pitching.get("wildPitches", 0)
            values["balks"] = pitching.get("balks", 0)
            values["pickoffs"] = pitching.get("pickoffs", 0)
            values["inherited_runners"] = pitching.get("inheritedRunners", 0)
            values["inherited_runners_scored"] = pitching.get(
                "inheritedRunnersScored", 0
            )
            values["passed_ball"] = pitching.get("passedBall", 0)
            values["ground_outs"] = pitching.get("groundOuts", 0)
            values["fly_outs"] = pitching.get("flyOuts", 0)
            values["air_outs"] = pitching.get("airOuts", 0)
            values["pop_outs"] = pitching.get("popOuts", 0)
            values["line_outs"] = pitching.get("lineOuts", 0)
            values["doubles"] = pitching.get("doubles", 0)
            values["triples"] = pitching.get("triples", 0)
            values["rbi"] = pitching.get("rbi", 0)
            values["sac_bunts"] = pitching.get("sacBunts", 0)
            values["sac_flies"] = pitching.get("sacFlies", 0)
            values["catchers_interference"] = pitching.get("catchersInterference", 0)
            values["stolen_bases"] = pitching.get("stolenBases", 0)
            values["caught_stealing"] = pitching.get("caughtStealing", 0)
            values["stolen_base_percentage"] = pitching.get("stolenBasePercentage")
            values["runs_scored_per_9"] = pitching.get("runsScoredPer9")
            values["home_runs_per_9"] = pitching.get("homeRunsPer9")

        return values
