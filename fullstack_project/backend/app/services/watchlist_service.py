import csv, os, tempfile
from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Any, List, Dict
from app.schemas.watchlist import WatchlistItem

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
BOOKS_PATH = os.path.join(DATA_DIR, "books.csv")
WATCHLIST_PATH = os.path.join(DATA_DIR, "watchlists.csv")
WATCHLIST_HEADERS = ["user_id", "isbn", "created_on"]

def _normalize_user_id(user: Any) -> str:
    if isinstance(user, str):
        return user
    if isinstance(user, dict):
        return str(user.get("userid") or user.get("user_id") or user.get("id") or "")
    return str(user)

def readCsv(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))
    
def writeCsv(path: str, headers: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(path),newline="", encoding="utf-8") as tmp:
        w = csv.DictWriter(tmp, fieldnames=headers, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmpPath = tmp.name
    os.replace(tmpPath, path)

def booksByIsbn() -> Dict[str, Dict[str, str]]:
    rows = readCsv(BOOKS_PATH)
    return {r["isbn"]: r for r in rows if r.get("isbn")}

def listWatchlist(userId: str) -> List[WatchlistItem]:
    userId = _normalize_user_id(userId)
    books = booksByIsbn()
    rows = readCsv(WATCHLIST_PATH)
    mine = [r for r in rows if r.get("user_id") == userId]
    mine.sort(key=lambda r: r.get("created_on") or "", reverse=True)
    items: List[WatchlistItem] = []
    for r in mine:
        b = books.get(r["isbn"])
        if not b:
            continue
        items.append(WatchlistItem(
            isbn=b.get("isbn",""),
            title=b.get("title",""),
            author=b.get("author"),
            year_of_publication=b.get("year_of_publication"),
            publisher=b.get("publisher"),
            img_url_s=b.get("img_url_s"),
            img_url_m=b.get("img_url_m"),
            img_url_l=b.get("img_url_l"),
        ))
    return items

def addBookToWatchlist(userId: str, isbn: str) -> WatchlistItem:
    userId = _normalize_user_id(userId)
    books = booksByIsbn()
    book = books.get(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="ISBN not found in books.csv")
    
    rows = readCsv(WATCHLIST_PATH)
    exists = any(r for r in rows if r.get("user_id") == userId and r.get("isbn") == isbn)
    if not exists:
        created_on = datetime.now(timezone.utc).date().isoformat()
        rows.append({"user_id": userId, "isbn": isbn, "created_on": created_on})
        writeCsv(WATCHLIST_PATH, WATCHLIST_HEADERS, rows)

    # return the added item
    return WatchlistItem(
        isbn=book.get("isbn",""),
        title=book.get("title",""),
        author=book.get("author"),
        year_of_publication=book.get("year_of_publication"),
        publisher=book.get("publisher"),
        img_url_s=book.get("img_url_s"),
        img_url_m=book.get("img_url_m"),
        img_url_l=book.get("img_url_l"),
    )

def removeBookFromWatchlist(userId: str, isbn: str) -> None:
    userId = _normalize_user_id(userId)
    rows = readCsv(WATCHLIST_PATH)
    new_rows = [r for r in rows if not (r.get("user_id") == userId and r.get("isbn") == isbn)]
    if len(new_rows) != len(rows):
        writeCsv(WATCHLIST_PATH, WATCHLIST_HEADERS, new_rows)
