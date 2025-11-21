from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import List
from app.repositories import ratedBooks_repo
from app.services import watchlist_service
from app.schemas.watchlist import WatchlistItem 


def listRatedBooks(user_id: str) -> List[WatchlistItem]:

    # Get rated books for the user
    rated = ratedBooks_repo.list_for_user(user_id)
    watchlist_items = watchlist_service.listWatchlist(user_id)
    by_isbn = {item.isbn: item for item in watchlist_items}
    results = []
    for entry in rated:
        item = by_isbn.get(entry["isbn"])
        if item:
            results.append(item)
    return results

# Add a rating for a book
def rateBook(user_id: str, isbn: str, score: int) -> None:
    if not 0 <= score <= 10:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 10")

    # Ensure the book is in the user's watchlist
    if isbn not in {item.isbn for item in watchlist_service.listWatchlist(user_id)}:
        raise HTTPException(status_code=400, detail="Book must be in your history before rating")

    # Check if the user has already rated this book
    if ratedBooks_repo.find(user_id, isbn):
        raise HTTPException(status_code=409, detail="You already rated this book")

    ratedBooks_repo.append({
        "user_id": user_id,
        "isbn": isbn,
        "score": str(score),
        "created_on": datetime.now(timezone.utc).date().isoformat(),
    })