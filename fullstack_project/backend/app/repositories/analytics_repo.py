from pathlib import Path
import csv, os
from typing import List, Dict, Any
from app.repositories import books_repo
# I had imported the books_repo for title lookup



DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "analytics.csv"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def save_all(books: List[Dict[str, Any]]) -> None:
    if not books:
        # If no items, remove the file or create an empty one with no data rows
        DATA_PATH.unlink(missing_ok=True)
        return

    fieldnames = list(books[0].keys())  # use keys from the first item as column names
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
    
    os.replace(tmp, DATA_PATH)

#  we got the title by its matching ISBN from the books_repo.py and then here we update our record of title .
if __name__ == "__main__":
    isbn_to_title = books_repo.get_isbn_title_map()
    record["title"] = isbn_to_title.get(record["book_id"], "Unknown")