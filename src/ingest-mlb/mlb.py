import asyncio
import os
from typing import Any, List

import httpx
from dotenv import load_dotenv

from common.decorators import retry

from models import GameInformation, Player, Team, TeamSchedules


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
            "weather": response.json().get("gameData", {}).get("weather", {}),
            "boxscore": response.json().get("liveData", {}).get("boxscore", {}),
        }
        for response in responses
    ]

    return game_info


def _extract_player_stats(players: dict) -> dict:
    return {}


def _extract_matchup_stats(matchup: dict) -> dict:
    return {}


def _extract_player_bios(players: dict) -> dict:
    return {}


async def _fetch_data(endpoint_type: str, extract_func, **kwargs):
    """Generic async function to fetch and extract data from any endpoint"""
    response = await _get_api_endpoints_and_params(
        endpoint_type=endpoint_type, **kwargs
    )
    return extract_func(response)


async def _get_games(start_date: str, end_date: str):
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
