import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import List, Optional
from app.schemas.book import Book, BookCreate, BookUpdate
from app.services.books_service import get_book_by_isbn, search_books, create_book, delete_book, update_book
from app.core.security import verify_access_token
from app.schemas.filter import Filter

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search/{title}", response_model=List[Book])
def search_book(title : str, filters : Filter = Depends()):
    return search_books(title, filter_data=filters)

#simple post the payload (is the body of the request)
@router.post("/create", response_model=Book, status_code=status.HTTP_201_CREATED)
async def post_book(payload: BookCreate, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return create_book(payload)

@router.get("/{isbn}", response_model=Book, status_code=status.HTTP_200_OK)
def get_book(isbn: str):
    return get_book_by_isbn(isbn)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/update/{isbn}", response_model=Book, status_code=status.HTTP_200_OK)
async def put_book(isbn: str, payload: BookUpdate, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return update_book(isbn, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/delete/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book(isbn : str, token_data : dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_book(isbn)
    return None

#Allows for a csv file upload for admin users to add many books at once
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_books_csv(file: UploadFile = File(...), token_data: dict = Depends(verify_access_token)):
    msg = ""
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        content = await file.read()
        csv_data = content.decode('latin-1')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not read or decode file: {e}")

    new_books = []
    csv_file = io.StringIO(csv_data)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        try:
            book_payload = BookCreate(**row)
            
            book = create_book(book_payload)
            new_books.append(book)
            
        except Exception as e:
            msg += f"Error processing row {row}: {e}\n"
            continue

    if not new_books:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="No valid books could be created from the CSV.")

    return {"message": f"Successfully created {len(new_books)} books.", "errors" : msg}