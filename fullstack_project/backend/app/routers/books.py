from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.book import Book, BookCreate, BookUpdate
from app.services.books_service import get_book_by_isbn, search_books, create_book, delete_book, update_book
from app.core.security import verify_access_token

router = APIRouter(prefix="/books", tags=["books"], dependencies=[Depends(verify_access_token)])

@router.get("/search/{title}", response_model=List[Book])
async def search_book(title : str):
    return search_books(title)

#simple post the payload (is the body of the request)
@router.post("", response_model=Book, status_code=201)
def post_book(payload: BookCreate):
    return create_book(payload)

@router.get("/{isbn}", response_model=Book)
def get_book(isbn: str):
    return get_book_by_isbn(isbn)

## We use put here because we are not creating an entirely new book, ie. we keep isbn the same
@router.put("/{isbn}", response_model=Book)
def put_book(isbn: str, payload: BookUpdate):
    return update_book(isbn, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(isbn: str):
    delete_book(isbn)
    return None