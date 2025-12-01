from pathlib import Path
import csv, os
from typing import List, Dict, Any
from functools import lru_cache

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "books.csv"

@lru_cache(maxsize=1)
def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []

    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        items = []
        append = items.append
        
        for row in reader:
            append(dict(zip(header, row)))

        return items

def save_all(books: List[Dict[str, Any]]) -> None:
    load_all.cache_clear()
    if not books:
        DATA_PATH.unlink(missing_ok=True)
        return

    fieldnames = list(books[0].keys())
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter= ";")
        writer.writeheader()
        writer.writerows(books)
    
    os.replace(tmp, DATA_PATH)
