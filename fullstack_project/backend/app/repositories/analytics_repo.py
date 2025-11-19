from pathlib import Path
from typing import List, Dict, Any

from app.utils.csv_utils import read_csv, write_csv

# I had imported the books_repo for title lookup

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "analytics.csv"
# i had created a utility file called csv_utils.py for reading and writing CSV files safely so that code is not duplicated across repositories.
# and i decideed to use that here in both load_all and save_all functions.

def load_all() -> List[Dict[str, Any]]:
    return read_csv(DATA_PATH)


def save_all(rows: List[Dict[str, Any]]) -> None:
    write_csv(DATA_PATH, rows)
