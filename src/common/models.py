from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class CustomModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
        json_encoders={Enum: lambda v: v.value},
        populate_by_name=True,
        validate_default=True,
        validate_assignment=True,
    )

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs)

        for key, value in data.items():
            if isinstance(value, list):
                data[key] = ", ".join(
                    map(lambda x: x.value if isinstance(x, Enum) else str(x), value)
                )
            elif isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, UUID):
                data[key] = str(value)

        return data
