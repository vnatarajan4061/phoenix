from datetime import datetime

from pydantic import field_serializer

from common.models import CustomModel


class TeamSchedules(CustomModel):
    team_id: int
    date: str
    opponent_id: int


@field_serializer(mode="before")
def serialize_date(cls, value: datetime.date) -> str:
    return value.strftime("%Y-%m-%d")
