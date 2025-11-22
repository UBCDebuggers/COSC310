from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.services.ratings_service import (
    get_ratings_by_userid,
    get_ratings_by_isbn,
    create_rating,
    delete_rating,
    update_rating
)

router = APIRouter(prefix="/ratings", tags=["ratings"])

#Creates a rating on a book for a loggedin user
@router.post("", response_model=Rating, status_code=201)
def post_rating(payload: RatingCreate, token_data: dict = Depends(verify_access_token)):
    return create_rating(payload, token_data["userid"])

#Gets all ratings belonging to a book
@router.get("/isbn/{isbn}", response_model=List[Rating])
def get_ratings_by_isbn(isbn: str):
    return get_ratings_by_isbn(isbn)

#Gets all ratings belonging to a user
@router.get("/userid/{userid}", response_model=List[Rating])
def get_rating_by_userid(userid: str):
    return get_ratings_by_userid(userid)

#Updates a user's rating
@router.put("/{isbn}", response_model=Rating)
def put_rating(isbn: str, payload: RatingUpdate, token_data: dict = Depends(verify_access_token)):
    return update_rating(isbn, token_data["userid"], payload)

#Deletes any specific rating
@router.delete("/{isbn}/{userid}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating_admin(isbn: str, userid: str, token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_rating(isbn, userid)
    return None

#Deletes the user who is loggedin's rating
@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating(isbn: str, token_data: dict = Depends(verify_access_token)):
    delete_rating(isbn, token_data["userid"])
    return None
