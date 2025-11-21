import csv, os, tempfile
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RATED_PATH = DATA_DIR / "ratedBooks.csv"
HEADERS = ["user_id", "isbn", "score", "created_on"]

# Helper functions to read and to write the rated books CSV file
def _read() -> List[Dict[str, str]]:
    if not RATED_PATH.exists():
        return []
    with RATED_PATH.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter=";"))

def _write(rows: List[Dict[str, str]]) -> None:
    os.makedirs(RATED_PATH.parent, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=RATED_PATH.parent, newline="", encoding="utf-8") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=HEADERS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
    os.replace(tmp_path, RATED_PATH)

# Repository functions
def find(user_id: str, isbn: str) -> Optional[Dict[str, str]]:
    return next((r for r in _read() if r["user_id"] == user_id and r["isbn"] == isbn), None)

def append(row: Dict[str, str]) -> None:
    rows = _read()
    rows.append(row)
    _write(rows)

def list_for_user(user_id: str) -> List[Dict[str, str]]:
    return [r for r in _read() if r["user_id"] == user_id]

def list_for_isbn(isbn: str) -> List[Dict[str, str]]:
    return [r for r in _read() if r["isbn"] == isbn]

def update_score(user_id: str, isbn: str, score: str, created_on: str) -> Optional[Dict[str, str]]:
    rows = _read()
    updated = None
    for row in rows:
        if row["user_id"] == user_id and row["isbn"] == isbn:
            row["score"] = score
            row["created_on"] = created_on
            updated = row
            break
    if updated:
        _write(rows)
    return updated

def remove(user_id: str, isbn: str) -> bool:
    rows = _read()
    new_rows = [r for r in rows if not (r["user_id"] == user_id and r["isbn"] == isbn)]
    if len(new_rows) == len(rows):
        return False
    _write(new_rows)
    return True
