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

@router.get("", response_model=List[WatchlistItem])
def getWatchlist(currUserId: dict = Depends(verify_access_token)):
    
    return listWatchlist(currUserId.get('userid'))

@router.post("", response_model=WatchlistItem, status_code=201)
def postWatchlistItem(payload: WatchlistAdd, currUserId: dict = Depends(verify_access_token)):
    
    return addBookToWatchlist(currUserId.get('userid'), payload.isbn)

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def removeWatchlistItem(isbn: str, currUserId: dict = Depends(verify_access_token)):

    removeBookFromWatchlist(currUserId.get('userid'), isbn)
    return None