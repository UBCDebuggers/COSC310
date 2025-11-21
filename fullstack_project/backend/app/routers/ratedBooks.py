from fastapi import APIRouter, Depends, status
from app.core.security import verify_access_token
from app.schemas.ratedBook import RatingCreate, RatedBook, RatingUpdate
from app.schemas.watchlist import WatchlistItem
from app.services import ratedBooks_service

router = APIRouter(prefix="/rated-books", tags=["rated-books"])


@router.get("", response_model=list[RatedBook], summary="List my rated books")
def get_rated_books(current=Depends(verify_access_token)):
    return ratedBooks_service.listRatedBooks(current["userid"])


@router.get("/options", response_model=list[WatchlistItem], summary="Books you can rate")
def get_rateable_books(current=Depends(verify_access_token)):
    return ratedBooks_service.listRateableBooks(current["userid"])


@router.get("/isbn/{isbn}", response_model=list[RatedBook], summary="List ratings for a book")
def get_ratings_by_isbn(isbn: str, current=Depends(verify_access_token)):
    return ratedBooks_service.listRatingsByIsbn(isbn)


@router.get("/users/{user_id}", response_model=list[RatedBook], summary="List ratings for a user")
def get_ratings_by_user(user_id: str, current=Depends(verify_access_token)):
    return ratedBooks_service.listRatingsForUser(current, user_id)


@router.post("", response_model=RatedBook, status_code=status.HTTP_201_CREATED, summary="Rate a book")
def rate_book(payload: RatingCreate, current=Depends(verify_access_token)):
    return ratedBooks_service.rateBook(current["userid"], payload.isbn, payload.score)


@router.put("/{isbn}", response_model=RatedBook, summary="Update rating")
def update_rating(isbn: str, payload: RatingUpdate, current=Depends(verify_access_token), user_id: str | None = None):
    target_user = user_id or current["userid"]
    return ratedBooks_service.updateRating(target_user, isbn, payload.score, requester=current)


@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove my rating")
def delete_rating(isbn: str, current=Depends(verify_access_token), user_id: str | None = None):
    target_user = user_id or current["userid"]
    ratedBooks_service.removeRating(target_user, isbn, requester=current)
    return None


@router.delete("/users/{user_id}/{isbn}", status_code=status.HTTP_204_NO_CONTENT, summary="Admin remove rating")
def admin_delete_rating(user_id: str, isbn: str, current=Depends(verify_access_token)):
    ratedBooks_service.removeRatingAsAdmin(user_id, isbn, requester=current)
    return None
