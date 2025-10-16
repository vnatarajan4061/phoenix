import asyncio

from database.ingestion import ingest_schedules
from mlb import (
    process_schedules,
)

# ROUTINE_MAP = {
#     "process_schedules": process_schedules,
# }

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()

    # parser.add_argument("--process-schedules", action="store_true")
    count = asyncio.run(ingest_schedules(process_schedules("2025-07-01", "2025-07-01")))
    print(f"Inserted {count} schedules")
    # print(process_teams(season=2025))
    # print(process_players(season=2025))
    # print(process_game_information("2025-05-01", "2025-05-02"))
