from fastapi import APIRouter, Depends, status
from app.core.security import verify_access_token
from app.schemas.history import HistoryListResponse, ErrorResponse
from app.services.create_history_item import get_last_books, get_history_by_isbn, get_history_by_userid, delete_history_item

router = APIRouter(prefix="/history", tags=["history"])

# Get the last N books viewed by a user (default: last 10)
@router.get("/user/{userid}/last", response_model=HistoryListResponse,
            responses={404: {"model": ErrorResponse}})
def get_last_history_items(userid: str, limit: int = 10, token_data : dict = Depends(verify_access_token)):
    items = get_last_books(userid, limit)
    return HistoryListResponse(items=items)

# Get history by ISBN
@router.get("/isbn/{isbn}", response_model=HistoryListResponse,
            responses={404: {"model": ErrorResponse}})
def get_history_items_by_isbn(isbn: str, token_data : dict = Depends(verify_access_token)):
    items = get_history_by_isbn(isbn)
    return HistoryListResponse(items=items)

# Get all history by User ID
@router.get("/user/{userid}", response_model=HistoryListResponse,
            responses={404: {"model": ErrorResponse}})
def get_history_items_by_userid(userid: str, token_data : dict = Depends(verify_access_token)):
    items = get_history_by_userid(userid)
    return HistoryListResponse(items=items)

# Delete a specific history item
@router.delete("/delete/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {"model": ErrorResponse}})
def delete_history(item_id: str, token_data : dict = Depends(verify_access_token)):
    delete_history_item(item_id)