# Borrowings repository: manage CSV persistence for book loans.
from pathlib import Path
from typing import List, Dict, Any
from app.repositories.base_csv_repo import BaseCSVRepository

# Borrowing Storage
class BorrowingsRepository(BaseCSVRepository):    
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "borrowings.csv"
    FIELDNAMES = ["borrowid", "userid", "isbn", "borrowed_at", "due_at", "returned_at"]
    DATETIME_FIELDS = ["borrowed_at", "due_at", "returned_at"]

# Adds a new borrowing record in a dictionary
def add_borrowing(borrowid: str, userid: str, isbn: str, borrowed_at: str, due_at: str, returned_at: str = "") -> Dict[str, Any]:
    rows = BorrowingsRepository.load_all()
    new = {
        'borrowid': borrowid,
        'userid': userid,
        'isbn': isbn,
        'borrowed_at': borrowed_at,
        'due_at': due_at,
        'returned_at': returned_at
    }
    rows.append(new)
    BorrowingsRepository.save_all(rows)
    return new

# Retrieves all borrowing records and returns the list
def get_all_borrowings() -> List[Dict[str, Any]]:
    return BorrowingsRepository.load_all()
