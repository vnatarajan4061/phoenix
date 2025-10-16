import asyncio
import os
from enum import Enum
from typing import Any, List, Type, Union

import httpx
from dotenv import load_dotenv
from jsonpath_ng.ext import parse

from common.decorators import retry

from models import (
    BatterGameLog,
    GameInformation,
    PitcherGameLog,
    Player,
    Team,
    TeamSchedules,
)


class GameLogType(str, Enum):
    """Enum for game log types with model mappings"""

    BATTING = "batting"
    PITCHING = "pitching"

    @property
    def model(self) -> Type[Union[BatterGameLog, PitcherGameLog]]:
        """Get the Pydantic model for this log type"""
        mapping = {
            GameLogType.BATTING: BatterGameLog,
            GameLogType.PITCHING: PitcherGameLog,
        }
        return mapping[self]

    @property
    def stats_key(self) -> str:
        """Get the boxscore stats key for this log type"""
        return self.value  # "batting" or "pitching"

    @property
    def player_list_key(self) -> str:
        """Get the boxscore player list key for this log type"""
        mapping = {
            GameLogType.BATTING: "batters",
            GameLogType.PITCHING: "pitchers",
        }
        return mapping[self]


@retry(attempts=3, calls_per_second=10)
async def _get_api_endpoints_and_params(endpoint_type: str, **kwargs) -> httpx.Response:
    load_dotenv()
    api_key: str = os.getenv("MLB_API")

    match endpoint_type:
        case "schedule":
            endpoint = "v1/schedule"
            params = {
                "startDate": kwargs.get("start_date"),
                "endDate": kwargs.get("end_date"),
                "sportId": 1,
                "gameType": kwargs.get("game_type", "R"),
                "hydrate": kwargs.get("hydrate", "venue,team, probablePitcher"),
            }
        case "game_information":
            game_id = kwargs.get("game_id")
            endpoint = f"v1.1/game/{game_id}/feed/live"
            params = {"hydrate": kwargs.get("hydrate", "boxscore,weather")}
        case "teams":
            endpoint = "v1/teams"
            params = {
                "sportId": 1,
                "season": kwargs.get(
                    "season", 2025
                ),  # This default probably should represent the actual year
            }
        case "players":
            endpoint = "v1/sports/1/players"
            params = {
                "season": kwargs.get("season", 2025),
                "gameType": kwargs.get("game_type", "R"),
            }
        case _:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        return await client.get(f"{api_key}/{endpoint}", params=params)


async def _fetch_data(endpoint_type: str, extract_func, **kwargs) -> Any:
    response = await _get_api_endpoints_and_params(
        endpoint_type=endpoint_type, **kwargs
    )
    return extract_func(response)


def _extract_teams(response: httpx.Response) -> List[dict[str, Any]]:
    return response.json().get("teams", [])


def _extract_players(response: httpx.Response) -> List[dict[str, Any]]:
    return response.json().get("people", [])


def _extract_team_schedules(response: httpx.Response) -> List[dict[str, Any]]:
    schedules = [
        {
            "game_date": date_item["date"],
            "game_id": game["gamePk"],
            "teams": game["teams"],
        }
        for date_item in response.json().get("dates", [])
        for game in date_item.get("games", [])
    ]
    return schedules


def _extract_game_information(
    responses: List[httpx.Response],
) -> List[dict[str, Any]]:
    game_info: List[dict[str, Any]] = [
        {
            "game_id": int(str(response.url).split("/game/")[1].split("/feed")[0]),
            "datetime": response.json().get("gameData", {}).get("datetime", {}),
            "status": response.json().get("gameData", {}).get("status", {}),
            "venue": response.json().get("gameData", {}).get("venue", {}),
            "teams": response.json().get("gameData", {}).get("teams", {}),
            "linescore": response.json().get("liveData", {}).get("linescore", {}),
            "weather": response.json().get("gameData", {}).get("weather", {}),
            "boxscore": response.json().get("liveData", {}).get("boxscore", {}),
        }
        for response in responses
    ]

    return game_info


async def _get_games(start_date: str, end_date: str) -> List[dict[str, Any]]:
    """Async function to get game information for a date range"""
    # Get schedules first
    schedules = await _fetch_data(
        endpoint_type="schedule",
        extract_func=_extract_team_schedules,
        start_date=start_date,
        end_date=end_date,
    )

    # Gather all game API calls concurrently
    game_responses = await asyncio.gather(
        *[
            _get_api_endpoints_and_params(
                endpoint_type="game_information", game_id=schedule["game_id"]
            )
            for schedule in schedules
        ]
    )

    # Extract data from all responses
    return _extract_game_information(game_responses)


def _extract_game_logs_from_boxscore(
    game_data: dict[str, Any], log_type: GameLogType
) -> List[dict[str, Any]]:
    game_id = game_data.get("game_id")
    boxscore = game_data.get("boxscore", {})

    logs = []

    # JSONPath to get all players with the specific stats type
    # For batting: finds all players where stats.batting exists
    # For pitching: finds all players where stats.pitching exists
    player_jsonpath = parse(f"$.teams[*].players.*[?stats.{log_type.stats_key}]")

    # Find all matching players across both teams
    player_matches = player_jsonpath.find(boxscore)

    for match in player_matches:
        player = match.value

        # Determine which team (home/away) this player is on
        # Navigate up the JSON tree to find team context
        path_parts = str(match.full_path).split(".")
        team_type = (
            path_parts[1].replace("teams[", "").replace("]", "").strip("'")
        )  # Extract 'home' or 'away'

        team_data = boxscore["teams"][team_type]
        team_id = team_data["team"]["id"]
        is_home = team_type == "home"

        # Get opponent
        opponent_type = "away" if team_type == "home" else "home"
        opponent_team_id = boxscore["teams"][opponent_type]["team"]["id"]

        log = {
            "gamePk": game_id,
            "playerId": player["person"]["id"],
            "teamId": team_id,
            "opponentTeamId": opponent_team_id,
            "isHome": is_home,
            "position": player.get("position"),
            "stats": player["stats"],
        }
        logs.append(log)

    return logs


def process_teams(season: int) -> List[Team]:
    """Process teams and return validated models"""
    extracted_data = asyncio.run(
        _fetch_data(endpoint_type="teams", extract_func=_extract_teams, season=season)
    )

    return [Team.model_validate(team) for team in extracted_data]


def process_players(season: int) -> List[Player]:
    """Process players and return validated models"""
    extracted_data = asyncio.run(
        _fetch_data(
            endpoint_type="players", extract_func=_extract_players, season=season
        )
    )

    return [Player.model_validate(player) for player in extracted_data]


def process_schedules(start_date: str, end_date: str) -> List[TeamSchedules]:
    """Process team schedules and return validated models"""
    extracted_data = asyncio.run(
        _fetch_data(
            endpoint_type="schedule",
            extract_func=_extract_team_schedules,
            start_date=start_date,
            end_date=end_date,
        )
    )

    return [TeamSchedules.model_validate(schedule) for schedule in extracted_data]


def process_game_information(start_date: str, end_date: str) -> List[GameInformation]:
    """Process game information and return validated models"""
    extracted_data = asyncio.run(_get_games(start_date, end_date))

    return [GameInformation.model_validate(game) for game in extracted_data]


def process_game_logs(
    start_date: str, end_date: str, log_type: GameLogType
) -> Union[List[BatterGameLog], List[PitcherGameLog]]:
    # Reuse _get_games to fetch all game data
    games_data = asyncio.run(_get_games(start_date, end_date))

    # Extract logs from each game and flatten
    all_logs = []
    for game_data in games_data:
        logs = _extract_game_logs_from_boxscore(game_data, log_type)
        all_logs.extend(logs)

    # Validate with appropriate Pydantic model
    validated_logs = [log_type.model.model_validate(log) for log in all_logs]

    return validated_logs
