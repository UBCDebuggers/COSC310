from typing import List
from fastapi import HTTPException
from app.schemas.history import HistoryItem
from app.repositories import history_repo

def create_history(userid: str, isbn: str) -> HistoryItem:
    # Keeps record of a book that a student opened
    new_item = history_repo.add_history_item(userid, isbn)
    return HistoryItem(**new_item)

def get_last_books(userid: str, limit: int = 10) -> List[HistoryItem]:
    # Get the last 10 books a student opened
    items = get_history_by_userid(userid)
    # Sorts by date time descending
    sorted_items = sorted(items, key=lambda it: it.date, reverse=True)
    return sorted_items[:limit]

def get_history_by_isbn(isbn: str) -> List[HistoryItem]:
    # Return all history items that match the given ISBN; will raise an error if there is none found
    records = history_repo.load_all()
    found: List[HistoryItem] = []
    for rec in records:
        if rec.get("isbn") == isbn:
            found.append(HistoryItem(**rec))
    if not found:
        raise HTTPException(status_code=404, detail=f"History for ISBN '{isbn}' not found")
    return found

def get_history_by_userid(userid: str) -> List[HistoryItem]:
    # Return all history items for the given Id; will raise an error if there is none found"""
    records = history_repo.load_all()
    found: List[HistoryItem] = []
    for rec in records:
        if rec.get("userid") == userid:
            found.append(HistoryItem(**rec))
    if not found:
        raise HTTPException(status_code=404, detail=f"History for UserID '{userid}' not found")
    return found

def delete_history_item(item_id: str) -> None:
    # Delete a specific history item
    if not history_repo.delete_history_item(item_id):
        raise HTTPException(status_code=404, detail=f"History item '{item_id}' not found")