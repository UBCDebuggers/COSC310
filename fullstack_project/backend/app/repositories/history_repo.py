from pathlib import Path
import csv, os
from typing import List, Dict, Any
from datetime import datetime, timezone

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "history.csv"

# Load all history items
def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []

    items: List[Dict[str, Any]] = []
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if 'date' in row and row['date']:
                try:
                    row['date'] = datetime.fromisoformat(row['date'])
                except Exception:
                    pass
            items.append(row)

    return items

# Save all history items
def save_all(items: List[Dict[str, Any]]) -> None:
    if not items:
        DATA_PATH.unlink(missing_ok=True)
        return
    serializable = []
    for row in items:
        r = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in row.items()}
        serializable.append(r)

    fieldnames = ["userid", "isbn", "date"]
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(serializable)
    
    os.replace(tmp, DATA_PATH)

# Add a new history item for a book the student opened
def add_history_item(userid: str, isbn: str) -> Dict[str, Any]:
    items = load_all()
    
    new_item = {
        "userid": userid,
        "isbn": isbn,
        "date": datetime.now(timezone.utc).isoformat()  # To avoid timezone ambiguity
    }
    
    items.append(new_item)
    save_all(items)
    return new_item

# Get the last 10 books opened by a student
def get_last_books(userid: str, n: int = 10) -> List[Dict[str, Any]]:
    items = load_all()
    user_items = [item for item in items if item.get("userid") == userid]
    return sorted(user_items, key=lambda x: x.get("date", ""), reverse=True)[:n]

# Delete a history item
def delete_history_item(userid: str, item_id: str) -> bool:
    items = load_all()
    filtered = [item for item in items if item.get("isbn") != item_id and item.get("id") != item_id]
    if len(filtered) < len(items):
        save_all(filtered)
        return True
    return False