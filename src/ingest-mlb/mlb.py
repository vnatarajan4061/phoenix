import os
from typing import Any, List

import pandas as pd
import requests
from dotenv import load_dotenv

from models import GameInformation, TeamSchedules


def _get_api_endpoints_and_params(endpoint_type: str, **kwargs) -> requests.Response:
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

        case _:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")

    return requests.get(f"{api_key}/{endpoint}", params=params)


def _extract_team_schedules(response: requests.Response) -> List[dict[str, Any]]:
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
    responses: List[requests.Response],
) -> List[dict[str, Any]]:
    game_info: List[dict[str, Any]] = [
        {
            "game_id": int(response.url.split("/game/")[1].split("/feed")[0]),
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


def process_schedules(start_date: str, end_date: str) -> pd.DataFrame:
    params: dict = {"start_date": start_date, "end_date": end_date}

    response: requests.Response = _get_api_endpoints_and_params(
        endpoint_type="schedule", **params
    )

    schedules: pd.DataFrame = pd.DataFrame.from_records(
        [
            TeamSchedules.model_validate(schedule).model_dump()
            for schedule in _extract_team_schedules(response)
        ],
    )

    return schedules


def process_game_information(start_date: str, end_date: str) -> pd.DataFrame:
    params: dict = {"start_date": start_date, "end_date": end_date}

    response: requests.Response = _get_api_endpoints_and_params(
        endpoint_type="schedule", **params
    )

    schedules = _extract_team_schedules(response)

    game_endpoints: List[requests.Response] = [
        _get_api_endpoints_and_params(
            endpoint_type="game_information", game_id=schedule["game_id"]
        )
        for schedule in schedules
    ]

    game_information: pd.DataFrame = pd.DataFrame.from_records(
        [
            GameInformation.model_validate(game).model_dump()
            for game in _extract_game_information(game_endpoints)
        ],
    )

    return game_information
