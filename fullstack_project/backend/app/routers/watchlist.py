from fastapi import APIRouter, Depends, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.user import User 
from app.schemas.watchlist import WatchlistItem, WatchlistAdd
from app.services.watchlist_service import (
    listWatchlist,
    addBookToWatchlist,
    removeBookFromWatchlist,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"], dependencies=[Depends(verify_access_token)])

@router.get("", response_model=List[WatchlistItem], summary="Get watchlist")
def getWatchlist(currUser: dict = Depends(verify_access_token)):
    # Return the user's watchlist in order.
    return listWatchlist(currUser["userid"])

@router.post("", response_model=WatchlistItem, status_code=201, summary="Add to watchlist")
def postWatchlistItem(payload: WatchlistAdd, currUser: dict = Depends(verify_access_token)):
    # Add an ISBN to the user's watchlist.
    return addBookToWatchlist(currUser["userid"], payload.isbn)

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove from watchlist")
def removeWatchlistItem(isbn: str, currUser: dict = Depends(verify_access_token)):
    # Remove an ISBN from the user's watchlist.
    removeBookFromWatchlist(currUser["userid"], isbn)
    return None
