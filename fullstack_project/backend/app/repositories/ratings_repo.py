from pathlib import Path
from typing import List, Dict, Any
# Using the shared CSV helper functions so this repo doesn't
# need to manually handle DictReader/DictWriter boilerplate.
# This keeps the logic more consistent across repos.
from app.utils.csv_utils import read_csv, write_csv

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "ratings.csv"

# Delegating the CSV reading to the utility function  so this repo stays focused on ratings-specific behavior.
def load_all() -> List[Dict[str, Any]]:
    return read_csv(DATA_PATH)


def save_all(ratings: List[Dict[str, Any]]) -> None:
    write_csv(DATA_PATH, ratings)
