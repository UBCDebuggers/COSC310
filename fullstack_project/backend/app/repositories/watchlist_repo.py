from __future__ import annotations
import csv, os, tempfile, asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

wlLock = asyncio.Lock()


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BOOKS_PATH = os.path.join(DATA_DIR, "books.csv")
WATCHLISTS_PATH = os.path.join(DATA_DIR, "watchlists.csv")

def readCsv(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        return list(r)
    
def writeCsv(path: str, headers: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(path), newline="", encoding="utf-8") as tmp:
        w = csv.DictWriter(tmp, fieldnames=headers, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for row in rows:
            w.writerow(row)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmpPath = tmp.name
    os.replace(tmpPath, path)

def getBooksByIsbn() -> Dict[str, Dict[str, str]]:

    #Return the books by their isbn number

    rows = readCsv(BOOKS_PATH)
    
    byIsbn = {}
    for r in rows:
        if r.get("isbn"):
            byIsbn[r["isbn"]] = r
    return byIsbn

watchlistHeaders = ["user_id", "isbn", "created_on"]

def normalize_user_id(user: Any) -> str:
    if isinstance(user, str):
        return user
    if isinstance(user, dict):
        return str(user.get("userid") or user.get("user_id") or user.get("id") or "")
    return str(user)

def getWatchListIsbns (userId: str) -> List[str]:
    userId = normalize_user_id(userId)
    rows = readCsv(WATCHLISTS_PATH)
    mine = [r for r in rows if r.get("user_id") == userId]

    # used to sort the watchlist by creation date
    mine.sort(key=lambda r: r.get("created_on") or "", reverse=True)
    return [r["isbn"] for r in mine]

async def addToWatchlist(userId: str, isbn: str) -> List[str]:
    userId = normalize_user_id(userId)
    async with wlLock:
        rows = readCsv(WATCHLISTS_PATH)
        exists = any(r for r in rows if r.get("user_id") == userId and r.get("isbn") == isbn)
        if not exists:
            created_on = datetime.now(timezone.utc).date().isoformat()
            rows.append({"user_id": userId, "isbn": isbn, "created_on": created_on})
            writeCsv(WATCHLISTS_PATH, watchlistHeaders, rows)

        # return the updated list for the user
        mine = [r for r in rows if r.get("user_id") == userId]
        mine.sort(key=lambda r: r.get("created_on") or "", reverse=True)
        return [r["isbn"] for r in mine]
