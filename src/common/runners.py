import warnings
from argparse import Namespace
from typing import Any, Callable, Literal

from flask import Response, jsonify


def run_flags(
    routine_map: dict[str, Callable],
    args: tuple[Any, ...],
    flags: Namespace | None = None,
    suffixes: tuple[str, ...] = ("scatch",),
    suffix_mode: Literal["only"] | Literal["exclude"] = "exclude",
) -> tuple[Response | None, int]:
    warnings.filterwarnings("ignore")

    if flags is None or all(not getattr(flags, flag) for flag in routine_map):
        for flag, routine in routine_map.items():
            suffix_match = any(flag.endswith(suffix) for suffix in suffixes)

            if (suffix_mode == "only") == suffix_match:
                routine(*args)

    else:
        for flag, routine in routine_map.items():
            if getattr(flags, flag):
                routine(*args)

    try:
        return jsonify({"Message": "OK"}), 200
    except RuntimeError:
        return None, 200
