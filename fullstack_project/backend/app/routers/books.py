from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.book import Book, BookCreate, BookUpdate
from app.services.books_service import get_book_by_isbn, list_books, create_book, delete_book, update_book
from app.core.security import verify_access_token

router = APIRouter(prefix="/books", tags=["books"], dependencies=[Depends(verify_access_token)])

@router.get("", response_model=List[Book])
def get_Books():
    return list_books()

#simple post the payload (is the body of the request)
@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
def post_book(payload: BookCreate, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return create_book(payload)

@router.get("/{isbn}", response_model=Book, status_code=status.HTTP_200_OK)
def get_book(isbn: str):
    return get_book_by_isbn(isbn)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{isbn}", response_model=Book, status_code=status.HTTP_200_OK)
def put_book(isbn: str, payload: BookUpdate, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return update_book(isbn, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(isbn : str, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_book(isbn)
    return None