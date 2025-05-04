import pandas as pd


def convert_to_datetime(date_str: str) -> pd.Timestamp:
    """
    Convert a date string to a pandas Timestamp object.
    """
    try:
        return pd.to_datetime(date_str)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")
