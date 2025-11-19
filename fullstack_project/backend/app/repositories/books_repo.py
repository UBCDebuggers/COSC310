from pathlib import Path
from typing import List, Dict, Any
from app.utils.csv_utils import read_csv, write_csv
# Using the shared CSV helpers to avoid repeating DictReader/Writer boilerplate.
# Books uses a custom delimiter + encoding, so we pass those as parameters.


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "books.csv"

# Reuse the shared CSV reader but keep books.csv-specific settings.
def load_all() -> List[Dict[str, Any]]:
   return read_csv(DATA_PATH, delimiter=';', encoding='latin-1')

def save_all(books: List[Dict[str, Any]]) -> None:
    write_csv(DATA_PATH, books, delimiter=';', encoding='latin-1')

# this two functions are used for setting the title in analytics.csv be aggregated from the books.csv , using the ISBN . 
# I dont think i will need to refactor them to use the shared csv utils since they are very specific to this repo.

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