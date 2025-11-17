# Waitlist repository: manage CSV persistence for book waitlist entries
from pathlib import Path
import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from app.repositories.base_csv_repo import BaseCSVRepository

# Waitlist Storage
class WaitlistRepository(BaseCSVRepository):    
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "waitlist.csv"
    FIELDNAMES = ["waitlistid", "userid", "isbn", "email", "joined_at"]
    DATETIME_FIELDS = ["joined_at"]

# Adds a user to waitlist
def add_to_waitlist(userid: str, isbn: str, email: str) -> Dict[str, Any]:
    entries = WaitlistRepository.load_all()
    new = {
        "waitlistid": str(uuid.uuid4()),
        "userid": userid,
        "isbn": isbn,
        "email": email,
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    entries.append(new)
    WaitlistRepository.save_all(entries)
    return new

# Get all waitlist entries for a specific ISBN
def get_waitlist_for_isbn(isbn: str) -> List[Dict[str, Any]]:
    entries = WaitlistRepository.load_all()
    return [e for e in entries if e.get('isbn') == isbn]

# Remove a user from the waitlist
def remove_waitlist_entry(waitlistid: str) -> bool:
    entries = WaitlistRepository.load_all()
    filtered = [e for e in entries if e.get('waitlistid') != waitlistid]
    if len(filtered) < len(entries):
        WaitlistRepository.save_all(filtered)
        return True
    return False

# Get methods for user waitlists
def get_waitlists_for_user(userid: str) -> List[Dict[str, Any]]:
    entries = WaitlistRepository.load_all()
    return [e for e in entries if e.get("userid") == userid]

# Delete all waitlist entries for a specific user
def delete_waitlists_for_user(userid: str) -> int:
    entries = WaitlistRepository.load_all()
    filtered = [e for e in entries if e.get("userid") != userid]
    deleted = len(entries) - len(filtered)
    if deleted > 0:
        WaitlistRepository.save_all(filtered)
    return deleted

# Delete all waitlist entries for a specific book
def delete_waitlists_for_book(isbn: str) -> int:
    entries = WaitlistRepository.load_all()
    filtered = [e for e in entries if e.get("isbn") != isbn]
    deleted = len(entries) - len(filtered)
    if deleted > 0:
        WaitlistRepository.save_all(filtered)
    return deleted
