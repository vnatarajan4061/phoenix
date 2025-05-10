import os
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from models import TeamSchedules


def _extract_team_schedules(response: requests.Response) -> pd.DataFrame:
    schedules = pd.DataFrame(
        [
            TeamSchedules.model_validate(
                {"game_date": date_item["date"], "game_pk": game["gamePk"]}
            ).model_dump()
            for date_item in response.json().get("dates", [])
            for game in date_item.get("games", [])
        ]
    )
    return schedules


def _extract_player_stats(players: dict) -> dict:
    return {}


def _extract_matchup_stats(matchup: dict) -> dict:
    return {}


def _extract_player_bios(players: dict) -> dict:
    return {}


def process_schedules(start_date: str, end_date: str) -> dict:
    load_dotenv()
    api_key: str = os.getenv("MLB_API")
    endpoint: str = "v1/schedule"
    params: dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "sportId": 1,
        "gameType": "R",
        "hydrate": "venue,team",
    }

    response: requests.Response = requests.get(f"{api_key}/{endpoint}", params=params)

    return _extract_team_schedules(response)
