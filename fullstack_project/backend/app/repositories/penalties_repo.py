from pathlib import Path
import csv, os
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "penalties.csv"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    
    with DATA_PATH.open("r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter= ";")
        return [row for row in reader]

def save_all(record: List[Dict[str, Any]]) -> None:
    if not record:
        DATA_PATH.unlink(missing_ok=True)
        return

    fieldnames = list(record[0].keys())
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter= ";")
        writer.writeheader()
        writer.writerows(record)
    
    os.replace(tmp, DATA_PATH)
