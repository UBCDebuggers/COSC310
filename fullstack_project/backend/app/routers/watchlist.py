from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.penalties import LIMITED_ACTIONS
from app.schemas.user import User 
from app.schemas.watchlist import WatchlistItem, WatchlistAdd
from app.services.library_service import check_restrictions
from app.services.penalties_service import get_penalties_for_user
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
    check_restrictions(currUserId.get('userid'), "You are restricted from creating watchlists.")
    return addBookToWatchlist(currUserId.get('userid'), payload.isbn)

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def removeWatchlistItem(isbn: str, currUserId: dict = Depends(verify_access_token)):

    removeBookFromWatchlist(currUserId.get('userid'), isbn)
    return None