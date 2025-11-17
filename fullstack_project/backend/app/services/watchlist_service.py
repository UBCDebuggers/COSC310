import csv, os, tempfile
from datetime import datetime, timezone
from fastapi import HTTPException
from typing import List, Dict
from app.schemas.watchlist import WatchlistItem

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
BOOKS_PATH = os.path.join(DATA_DIR, "books.csv")
WATCHLIST_PATH = os.path.join(DATA_DIR, "watchlists.csv")
WATCHLIST_HEADERS = ["user_id", "isbn", "created_on"]
DATE_FORMAT = "%Y-%m-%d"

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

def looksLikeUnixTimestamp(value: str) -> bool:
    candidate = value.strip()
    if not candidate:
        return False
    if candidate.startswith("-"):
        candidate = candidate[1:]
    return candidate.replace(".", "", 1).isdigit()

def normalizeWatchlistRows(rows: List[Dict[str, str]]) -> bool:
    changed = False
    for row in rows:
        created_value = row.get("created_on", "").strip()
        if not created_value:
            legacy_value = row.pop("created_at", "").strip()
            if legacy_value:
                row["created_on"] = legacy_value
                created_value = legacy_value
                changed = True
        if created_value and looksLikeUnixTimestamp(created_value):
            try:
                iso = datetime.fromtimestamp(float(created_value), tz=timezone.utc).date().isoformat()
            except ValueError:
                continue
            if iso != created_value:
                row["created_on"] = iso
                changed = True
    return changed

def loadWatchlistRows() -> List[Dict[str, str]]:
    rows = readCsv(WATCHLIST_PATH)
    if normalizeWatchlistRows(rows):
        writeCsv(WATCHLIST_PATH, WATCHLIST_HEADERS, rows)
    return rows

def parseCreatedOn(value: str) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.strptime(value, DATE_FORMAT)
        return parsed.replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid watchlist created_on format: {value}") from exc

def listWatchlist(userId: str) -> List[WatchlistItem]:
    books = booksByIsbn()
    rows = loadWatchlistRows()
    mine = [r for r in rows if r.get("user_id") == userId]
    mine.sort(key=lambda r: parseCreatedOn(r.get("created_on", "")), reverse=True)
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
    books = booksByIsbn()
    book = books.get(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="ISBN not found in books.csv")

    rows = loadWatchlistRows()
    exists = any(r for r in rows if r.get("user_id") == userId and r.get("isbn") == isbn)
    if not exists:
        rows.append({
            "user_id": userId,
            "isbn": isbn,
            "created_on": datetime.now(timezone.utc).date().isoformat(),
        })
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
    rows = loadWatchlistRows()
    new_rows = [r for r in rows if not (r.get("user_id") == userId and r.get("isbn") == isbn)]
    if len(new_rows) != len(rows):
        writeCsv(WATCHLIST_PATH, WATCHLIST_HEADERS, new_rows)
