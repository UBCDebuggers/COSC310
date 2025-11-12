from pathlib import Path
import csv, os
from typing import List, Dict, Any
from datetime import datetime, timezone

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "history.csv"

def load_all() -> List[Dict[str, Any]]:
    # Load all history items
    if not DATA_PATH.exists():
        return []

    items: List[Dict[str, Any]] = []
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Try to parse the date field into a datetime. If parsing fails, leave the raw string.
            if 'date' in row and row['date']:
                try:
                    row['date'] = datetime.fromisoformat(row['date'])
                except Exception:
                    # keep as-is if parse fails
                    pass
            items.append(row)

    return items

def save_all(items: List[Dict[str, Any]]) -> None:
    # Save all history items
    if not items:
        DATA_PATH.unlink(missing_ok=True)
        return

    # Ensure any datetime objects are converted to ISO strings before writing
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

def add_history_item(userid: str, isbn: str) -> Dict[str, Any]:
    # Add a new history item for a book the student opened
    items = load_all()
    
    new_item = {
        "userid": userid,
        "isbn": isbn,
        "date": datetime.now(timezone.utc).isoformat()  # To avoid timezone ambiguity
    }
    
    items.append(new_item)
    save_all(items)
    return new_item

def get_last_books(userid: str, n: int = 10) -> List[Dict[str, Any]]:
    # Get the last 10 books opened by a student
    items = load_all()
    user_items = [item for item in items if item.get("userid") == userid]
    # Sort by date descending and take the last n
    return sorted(user_items, key=lambda x: x.get("date", ""), reverse=True)[:n]

def delete_history_item(userid: str, item_id: str) -> bool:
    # Delete a history item
    items = load_all()
    filtered = [item for item in items if item.get("isbn") != item_id and item.get("id") != item_id]
    if len(filtered) < len(items):
        save_all(filtered)
        return True
    return False