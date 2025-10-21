from fastapi import APIRouter, status
from typing import List
from schemas.book import Book, BookCreate, BookUpdate
from services.books_service import get_book_by_isbn, list_books, create_book, delete_book, update_book

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=List[Book])
def get_Books():
    return list_books()

#simple post the payload (is the body of the request)
@router.post("", response_model=Book, status_code=201)
def post_book(payload: BookCreate):
    return create_book(payload)

from services.items_service import list_items, create_item, get_item_by_id

@router.get("/{isbn}", response_model=Book)
def get_book(isbn: str):
    return get_book_by_isbn(isbn)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{isbn}", response_model=Book)
def put_book(isbn: str, payload: BookUpdate):
    return update_book(isbn, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(isbn: str):
    delete_book(isbn)
    return None