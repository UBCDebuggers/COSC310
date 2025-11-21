from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.services.ratings_service import get_rating_by_isbn, list_ratings, create_rating, delete_rating, update_rating

router = APIRouter(prefix="/ratings", tags=["ratings"], dependencies=[Depends(verify_access_token)])

@router.get("", response_model=List[Rating])
def get_Ratings():
    return list_ratings()

#simple post the payload (is the body of the request)
@router.post("", response_model=Rating, status_code=201)
def post_rating(payload: RatingCreate, token_data: dict = Depends(verify_access_token)):
    return create_rating(payload, token_data["sub"])


@router.get("/isbn/{isbn}", response_model=List)
def get_rating_by_isbn(isbn: str):
    return get_rating_by_isbn(isbn)

@router.get("/userid/{id}", response_model=List)
def get_rating_by_id(id: str):
    return get_rating_by_id(id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{isbn}", response_model=Rating)
def put_rating(isbn: str, id: str, payload: RatingUpdate, token_data : dict = Depends(verify_access_token)):
    return update_rating(isbn, token_data['user'], payload)

## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{isbn}/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating_admin(isbn : str, id: str, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"] :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_rating(isbn, id)
    return None

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating(isbn : str, token_data : dict = Depends(verify_access_token)):
    delete_rating(isbn, token_data['user'])
    return None
