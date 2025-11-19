from typing import List
from fastapi import HTTPException
from statistics import mean
from collections import defaultdict
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.repositories.ratings_repo import load_all, save_all

def _load_raw_ratings():
    return load_all()

# Another simple helper that turns raw dicts into Rating objects, handling any necessary field renaming.
# this helper has to look for wtv is within ratingId so like the id field in the csv has to be mapped to ratingId in the model
def _as_models(raw_list):
    cleaned = []
    for r in raw_list:
            # If CSV contains "id", rename it to "ratingid"
            if "id" in r and "ratingid" not in r:
                r = {**r, "ratingid": r["id"]}

            cleaned.append(Rating(**r))

    return cleaned

def list_ratings() -> List[Rating]:
    return _as_models(_load_raw_ratings())


def create_rating(newRating: RatingCreate, userid: str) -> Rating:
    ratings = _load_raw_ratings()

    # Imma check if this user already rated this book
    for r in ratings:
        if r.get("id") == userid and r.get("isbn") == newRating.isbn:
            raise HTTPException(
                status_code=409,
                detail="Rating already exists for this user and book.",
            )


    new_record = Rating(
        ratingid=str(userid).strip(),
        isbn=newRating.isbn.strip(),
        rating=newRating.rating
    )

    ratings.append(new_record.model_dump())
    save_all(ratings)
    return new_record


def get_rating_by_isbn(rating_isbn: str) -> List[Rating]:
    ratings = _load_raw_ratings()
    found = []

    # Simple loop filtering (easy to read)
    for r in ratings:
        if r.get("isbn") == rating_isbn:
            found.append(Rating(**r))

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Rating for ISBN '{rating_isbn}' not found"
        )

    return found


def get_rating_by_id(rating_id: str) -> List[Rating]:
    ratings = _load_raw_ratings()
    found = []

    # Same logic as above, but for user ID
    for r in ratings:
        if r.get("id") == rating_id:
            found.append(Rating(**r))

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Rating for User-ID '{rating_id}' not found"
        )

    return found


def update_rating(rating_isbn: str, rating_id: str, ratingUpdate: RatingUpdate) -> Rating:
    ratings = _load_raw_ratings()

    for i, r in enumerate(ratings):
        if r.get("isbn") == rating_isbn and r.get("id") == rating_id:

            # Build updated rating model
            updated = Rating(
                isbn=rating_isbn,
                id=rating_id,
                rating=ratingUpdate.rating.strip()
            )

            ratings[i] = updated.model_dump()
            save_all(ratings)
            return updated

    raise HTTPException(
        status_code=404,
        detail=f"Rating '{rating_isbn}', '{rating_id}' not found"
    )


def delete_rating(rating_isbn: str, rating_id: str) -> None:
    ratings = _load_raw_ratings()

    # Keep everything except the one we want to delete
    new_ratings = [
        r for r in ratings
        if not (r.get("isbn") == rating_isbn and r.get("id") == rating_id)
    ]

    if len(new_ratings) == len(ratings):
        raise HTTPException(
            status_code=404,
            detail=f"Rating '{rating_isbn}', '{rating_id}' not found"
        )

    save_all(new_ratings)


def get_ratings_summary() -> dict:
    ratings = _load_raw_ratings()
    summary = defaultdict(list)

    # Collect all rating values grouped by ISBN
    for r in ratings:
        isbn = r.get("isbn")
        if not isbn:
            continue

        try:
            val = float(r.get("rating"))
            summary[isbn].append(val)
        except (TypeError, ValueError):
            continue

    # Build final summary
    result = {}
    for isbn, values in summary.items():
        result[isbn] = {
            "count": len(values),
            "avg": round(mean(values), 2),
        }

    return result


def get_unique_users_by_isbn() -> dict:
    ratings = _load_raw_ratings()
    users = defaultdict(set)

    # Map: ISBN → set of user IDs who rated it
    for r in ratings:
        isbn = r.get("isbn")
        uid = r.get("id") or r.get("user_id")

        if isbn and uid:
            users[isbn].add(uid)

    # Convert sets to lists for JSON
    return {isbn: list(uids) for isbn, uids in users.items()}
