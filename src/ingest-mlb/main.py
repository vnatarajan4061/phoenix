import argparse

from mlb import process_schedules

ROUTINE_MAP = {
    "process_schedules": process_schedules,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--process-schedules", action="store_true")
