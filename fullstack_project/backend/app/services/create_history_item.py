from typing import List
from fastapi import HTTPException
from app.schemas.history import HistoryItem
from app.repositories import history_repo

# Keeps record of a book that a student opened
def create_history(userid: str, isbn: str) -> HistoryItem:
    new_item = history_repo.add_history_item(userid, isbn)
    return HistoryItem(**new_item)

# Get the last 10 books a student opened and sorts by date time descending
def get_last_books(userid: str, limit: int = 10) -> List[HistoryItem]:
    items = get_history_by_userid(userid)
    sorted_items = sorted(items, key=lambda it: it.date, reverse=True)
    return sorted_items[:limit]

# Return all history items that match the given ISBN; will raise an error if there is none found
def get_history_by_isbn(isbn: str) -> List[HistoryItem]:
    records = history_repo.load_all()
    found: List[HistoryItem] = []
    for rec in records:
        if rec.get("isbn") == isbn:
            found.append(HistoryItem(**rec))
    if not found:
        raise HTTPException(status_code=404, detail=f"History for ISBN '{isbn}' not found")
    return found

# Return all history items for the given Id; will raise an error if there is none found"""
def get_history_by_userid(userid: str) -> List[HistoryItem]:
    records = history_repo.load_all()
    found: List[HistoryItem] = []
    for rec in records:
        if rec.get("userid") == userid:
            found.append(HistoryItem(**rec))
    if not found:
        raise HTTPException(status_code=404, detail=f"History for UserID '{userid}' not found")
    return found

# Delete a specific history item
def delete_history_item(item_id: str) -> None:
    if not history_repo.delete_history_item(item_id):
        raise HTTPException(status_code=404, detail=f"History item '{item_id}' not found")
    