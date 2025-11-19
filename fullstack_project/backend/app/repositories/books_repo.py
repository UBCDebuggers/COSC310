from pathlib import Path
import csv, os
from typing import List, Dict, Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "books.csv"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    
    with DATA_PATH.open("r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter= ";")
        return [row for row in reader]

def save_all(books: List[Dict[str, Any]]) -> None:
    if not books:
        # If no items, remove the file or create an empty one with no data rows
        DATA_PATH.unlink(missing_ok=True)
        return

    fieldnames = list(books[0].keys())  # use keys from the first item as column names
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter= ";")
        writer.writeheader()
        writer.writerows(books)
    
    os.replace(tmp, DATA_PATH)

# this two functions are used for setting the title in analytics.csv be aggregated from the books.csv , using the ISBN . 
def get_isbn_title_map() -> Dict[str, str]:
    books = load_all()
    isbn_title_map = {}

    for book in books:
        # Normalize possible column name variations
        isbn = book.get("isbn") or book.get("ISBN") or book.get("book_id")
        title = book.get("title") or book.get("Book-Title") or "Unknown"

        if isbn:
            isbn_title_map[isbn.strip()] = title.strip()
    
    return isbn_title_map

#  This function returns the title for a given ISBN. If not found, returns "Unknown".
def get_title_from_isbn(isbn: str) -> str:
    isbn_title_map = get_isbn_title_map()
    return isbn_title_map.get(isbn.strip(), "Unknown")