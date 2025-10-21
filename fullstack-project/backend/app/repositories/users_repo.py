from pathlib import Path
import csv, os
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "users.csv"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def save_all(books: List[Dict[str, Any]]) -> None:
    if not books:
        # If no items, remove the file or create an empty one with no data rows
        DATA_PATH.unlink(missing_ok=True)
        return

    fieldnames = list(books[0].keys())  # use keys from the first item as column names
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
    
    os.replace(tmp, DATA_PATH)
