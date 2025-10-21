from fastapi import APIRouter, status
from typing import List
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.services.ratings_service import get_rating_by_isbn, list_ratings, create_rating, delete_rating, update_rating

router = APIRouter(prefix="/ratings", tags=["ratings"])

@router.get("", response_model=List[Rating])
def get_Ratings():
    return list_ratings()

#simple post the payload (is the body of the request)
@router.post("", response_model=Rating, status_code=201)
def post_rating(payload: RatingCreate):
    return create_rating(payload)

@router.get("/isbn/{isbn}", response_model=List)
def get_rating_by_isbn(isbn: str):
    return get_rating_by_isbn(isbn)

@router.get("/userid/{id}", response_model=List)
def get_rating_by_id(id: str):
    return get_rating_by_id(id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{isbn}/{id}", response_model=Rating)
def put_rating(isbn: str, id: str, payload: RatingUpdate):
    return update_rating(isbn, id, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{isbn}/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rating(isbn: str, id: str):
    delete_rating(isbn, id)
    return None