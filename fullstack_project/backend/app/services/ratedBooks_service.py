from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import Dict, Iterable, List
from app.repositories import ratedBooks_repo
from app.schemas.ratedBook import RatedBook
from app.schemas.watchlist import WatchlistItem
from app.services import watchlist_service


def _normalize_user_id(user: Dict[str, object]) -> str:
    value = user.get("userid")
    if value is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return str(value)


def _is_admin(user: Dict[str, object]) -> bool:
    value = user.get("is_admin")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _books_by_isbn() -> Dict[str, Dict[str, str]]:
    return watchlist_service.booksByIsbn()


def _hydrate(rows: Iterable[Dict[str, str]]) -> List[RatedBook]:
    books = _books_by_isbn()
    items: List[RatedBook] = []
    for row in rows:
        book = books.get(row["isbn"], {})
        items.append(RatedBook(
            user_id=row["user_id"],
            isbn=row["isbn"],
            title=book.get("title"),
            author=book.get("author"),
            year_of_publication=book.get("year_of_publication"),
            publisher=book.get("publisher"),
            img_url_s=book.get("img_url_s"),
            img_url_m=book.get("img_url_m"),
            img_url_l=book.get("img_url_l"),
            score=int(row["score"]),
            created_on=row["created_on"],
        ))
    return items


def listRateableBooks(user_id: str) -> List[WatchlistItem]:
    return watchlist_service.listWatchlist(user_id)


def listRatedBooks(user_id: str) -> List[RatedBook]:
    return _hydrate(ratedBooks_repo.list_for_user(user_id))


def listRatingsByIsbn(isbn: str) -> List[RatedBook]:
    return _hydrate(ratedBooks_repo.list_for_isbn(isbn))


def listRatingsForUser(requester: Dict[str, object], target_user_id: str) -> List[RatedBook]:
    requester_id = _normalize_user_id(requester)
    if requester_id != target_user_id and not _is_admin(requester):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view that user's ratings")
    return listRatedBooks(target_user_id)


def _validate_score(score: int) -> None:
    if not 0 <= score <= 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Score must be between 0 and 10")


def _ensure_in_watchlist(user_id: str, isbn: str) -> None:
    if isbn not in {item.isbn for item in watchlist_service.listWatchlist(user_id)}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book must be in your watchlist to rate")


def rateBook(user_id: str, isbn: str, score: int) -> RatedBook:
    _validate_score(score)
    _ensure_in_watchlist(user_id, isbn)
    if ratedBooks_repo.find(user_id, isbn):
        raise HTTPException(status_code=409, detail="You already rated this book")

    ratedBooks_repo.append({
        "user_id": user_id,
        "isbn": isbn,
        "score": str(score),
        "created_on": datetime.now(timezone.utc).date().isoformat(),
    })
    return _hydrate(ratedBooks_repo.list_for_user(user_id))[-1]


def updateRating(user_id: str, isbn: str, score: int, requester: Dict[str, object]) -> RatedBook:
    _validate_score(score)
    requester_id = _normalize_user_id(requester)
    if requester_id != user_id and not _is_admin(requester):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit another user's rating")
    existing = ratedBooks_repo.find(user_id, isbn)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    updated = ratedBooks_repo.update_score(user_id, isbn, str(score), datetime.now(timezone.utc).date().isoformat())
    return _hydrate([updated])[0]


def removeRating(user_id: str, isbn: str, requester: Dict[str, object]) -> None:
    requester_id = _normalize_user_id(requester)
    if requester_id != user_id and not _is_admin(requester):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove another user's rating")
    if not ratedBooks_repo.remove(user_id, isbn):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")


def removeRatingAsAdmin(user_id: str, isbn: str, requester: Dict[str, object]) -> None:
    if not _is_admin(requester):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    if not ratedBooks_repo.remove(user_id, isbn):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
