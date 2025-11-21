from statistics import mean
from typing import List
from fastapi import HTTPException
from collections import defaultdict
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.repositories.ratings_repo import load_all, save_all

def list_ratings() -> List[Rating]:
    return [Rating(**attributes) for attributes in load_all()]

def create_rating(newRating: RatingCreate, userid : str) -> Rating:
    ratings = load_all()
    if any(rating.get("id") == userid and rating.get('isbn') == newRating.isbn for rating in ratings):
        raise HTTPException(status_code=409, detail="Rating collision; retry.")
    
    new_record = Rating(id = userid.strip(),
                      isbn = newRating.isbn.strip(),
                      rating = newRating.rating.strip(),
                      )
    ratings.append(new_record.model_dump())
    save_all(ratings)
    return new_record

def get_rating_by_isbn(rating_isbn: str) -> Rating:
    ratings = load_all()
    found = []
    for rating in ratings:
        if rating.get('isbn') == rating_isbn:
            found.append(Rating(**rating))
    if not found:
        raise HTTPException(status_code=404, detail=f"Rating for ISBN '{rating_isbn}' not found")
    return found

def get_rating_by_id(rating_id: str) -> Rating:
    found = []
    ratings = load_all()
    for rating in ratings:
        if rating.get('id') == rating_id:
            found.append(Rating(**rating))
    if not found:
        raise HTTPException(status_code=404, detail=f"Rating for User-ID '{rating_id}' not found")
    return found

def update_rating(rating_isbn: str, rating_id: str, ratingUpdate : RatingUpdate) -> Rating:
    ratings = load_all()
    for id, rating in enumerate(ratings):
        if rating.get("isbn") == rating_isbn:
            updated = Rating(isbn = rating_isbn,
                      id = rating_id,
                      rating = ratingUpdate.rating.strip(),
                      )
            ratings[id] = updated.model_dump()
            save_all(ratings)
            return updated
    raise HTTPException(status_code=404, detail=f"Rating '{rating_isbn}', '{rating_id}' not found")

def delete_rating(rating_isbn: str, rating_id: str) -> None:
    ratings = load_all()
    new_ratings = [
    r for r in ratings
    if not (r.get("isbn") == rating_isbn and r.get("id") == rating_id)
    ]
    if len(new_ratings) == len(ratings):
        HTTPException(status_code=404, detail=f"Rating '{rating_isbn}', '{rating_id}' not found")
    save_all(new_ratings)
        
            
    # added this function to get the count and average from the summary.
    
def get_ratings_summary() -> dict:
    ratings = load_all()
    summary = defaultdict(list)

    for r in ratings:
        isbn = r.get("isbn")
        if isbn:
            try:
                rating_value = float(r.get("rating"))
                summary[isbn].append(rating_value)
            except ValueError:
                continue

    result = {}
    for isbn, values in summary.items():
        result[isbn] = {
            "count": len(values),
            "avg": round(mean(values), 2)
        }
    return result

    #  This function returns a dictionary mapping ISBN to set of user IDs who rated it.
def get_unique_users_by_isbn() -> dict:
    ratings = load_all()
    user_map = defaultdict(set)

    for r in ratings:
        isbn = r.get("isbn")
        user_id = r.get("id") or r.get("user_id")
        if isbn and user_id:
            user_map[isbn].add(user_id)

    return {isbn: list(users) for isbn, users in user_map.items()}

# Sort books by rating_count (descending). Return top N.
def get_top_rated_books(n: int) -> List[dict]:
    rating_summary = get_ratings_summary()
    sorted_books = sorted(rating_summary.items(), key=lambda x: x[1]['count'], reverse=True)
    top_books = sorted_books[:n]
    
    result = []
    for isbn, data in top_books:
        result.append({
            "isbn": isbn,
            "rating_count": data['count'],
            "avg_rating": data['avg']
        })
    return result