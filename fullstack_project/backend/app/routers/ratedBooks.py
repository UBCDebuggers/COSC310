from fastapi import APIRouter, Depends, status
from app.core.security import verify_access_token
from app.schemas.ratedBook import RatingCreate
from app.services import ratedBooks_service
from app.schemas.watchlist import WatchlistItem

router = APIRouter(prefix="/rated-books", tags=["ratings"])

@router.get("", response_model=list[WatchlistItem], summary="List rated books")
def get_rated_books(current : dict=Depends(verify_access_token)):
    return ratedBooks_service.listRatedBooks(current.get('userid'))

@router.post("", status_code=status.HTTP_201_CREATED, summary="Rate a book")
def rate_book(payload: RatingCreate, current : dict =Depends(verify_access_token)):
    ratedBooks_service.rateBook(current.get('userid'), payload.isbn, payload.score)
    return {"message": "Rating saved"}