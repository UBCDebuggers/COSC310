from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.services.ratings_service import (
    get_rating_by_isbn,
    get_rating_by_id,
    list_ratings,
    create_rating,
    delete_rating,
    update_rating
)

router = APIRouter(prefix="/ratings", tags=["ratings"])

@router.get("", response_model=List[Rating])
def get_ratings(token_data: dict = Depends(verify_access_token)):
    # Returns all ratings stored in the system.
    return list_ratings()

@router.post("", response_model=Rating, status_code=201)
def post_rating(payload: RatingCreate, token_data: dict = Depends(verify_access_token)):
    # Creates a new rating for the logged-in user.
    return create_rating(payload, token_data["userid"])

@router.get("/isbn/{isbn}", response_model=List)
def get_rating_by_isbn_route(isbn: str, token_data: dict = Depends(verify_access_token)):
    # Returns all ratings for a specific book by ISBN.
    return get_rating_by_isbn(isbn)

@router.get("/userid/{id}", response_model=List)
def get_rating_by_id_route(id: str, token_data: dict = Depends(verify_access_token)):
    # Returns all ratings created by a specific user.
    return get_rating_by_id(id)

@router.put("/{isbn}", response_model=Rating)
def put_rating(isbn: str, payload: RatingUpdate, token_data: dict = Depends(verify_access_token)):
    # Updates an existing rating submitted by the logged-in user.
    return update_rating(isbn, token_data["userid"], payload)

@router.delete("/{isbn}/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating_admin(isbn: str, id: str, token_data: dict = Depends(verify_access_token)):
    # Admin-only: deletes any user’s rating for the given book.
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_rating(isbn, id)
    return None

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating(isbn: str, token_data: dict = Depends(verify_access_token)):
    # Deletes the logged-in user’s rating for the given book.
    delete_rating(isbn, token_data["userid"])
    return None
