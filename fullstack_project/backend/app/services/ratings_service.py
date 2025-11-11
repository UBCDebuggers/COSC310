from typing import List
from fastapi import HTTPException
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.repositories.ratings_repo import load_all, save_all

def list_ratings() -> List[Rating]:
    return [Rating(**attributes) for attributes in load_all()]

def create_rating(newRating: RatingCreate) -> Rating:
    ratings = load_all()
    if any(rating.get("id") == newRating.id & rating.get('isbn') == newRating.isbn for rating in ratings):
        raise HTTPException(status_code=409, detail="Rating collision; retry.")
    
    new_record = Rating(id = newRating.id.strip(),
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
    if found == None:
        raise HTTPException(status_code=404, detail=f"Rating for ISBN '{rating_isbn}' not found")
    return found

def get_rating_by_id(rating_id: str) -> Rating:
    found = []
    ratings = load_all()
    for rating in ratings:
        if ratings.get('id') == rating_id:
            found.append(Rating(**rating))
    if found == None:
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
    new_ratings = [rating for rating in ratings if rating.get("isbn") != rating_isbn & rating.get("id") != rating_id]
    if len(new_ratings) == len(ratings):
        HTTPException(status_code=404, detail=f"Rating '{rating_isbn}', '{rating_id}' not found")
    save_all(new_ratings)
        
            
    