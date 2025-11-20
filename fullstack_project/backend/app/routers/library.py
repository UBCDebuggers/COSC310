from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_access_token
from app.schemas.reservation import BookReservationCreate, BookReservation, RETURNED, NOT_RETURNED, RETURNED_OVERDUE, NOT_RETURNED_OVERDUE, CANCELLED
from app.services.library_service import borrow_book, return_book
from app.services.reservation_service import get_reservations_by_userid, update_reservation, get_latest_reservation_by_isbn, get_reservations_by_isbn, find_outstanding

router = APIRouter(prefix="/library", tags=["library"], dependencies= [Depends(verify_access_token)])

@router.post("/borrow", status_code= status.HTTP_200_OK, response_model=dict)
async def borrow(reservation_id : str, payload : BookReservationCreate, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return update_reservation(reservation_id, payload)
    else:
        return borrow_book(userid= current_user.get('userid'), isbn= payload.isbn, due_date= payload.expiry_date, is_admin= False)
    
@router.put("/return", status_code= status.HTTP_200_OK, response_model=dict)
async def book_return(userid : str, isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return return_book(userid, isbn)

@router.get("/userloans", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_user_loans(userid : str, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return get_reservations_by_userid(userid)
    return get_reservations_by_userid(current_user.get('userid'))

@router.get("/bookstatus/{isbn}", status_code= status.HTTP_200_OK, response_model=dict)
async def get_book_status(isbn : str):
    reservation = get_latest_reservation_by_isbn(isbn)
    if reservation.status in [RETURNED, RETURNED_OVERDUE, CANCELLED] or not reservation.active:
        return {"status" : "available"}
    elif reservation.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE]:
        return {"status" : "unavailable"}
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/bookhistory/{isbn}", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_book_history(isbn : str):
    return get_reservations_by_isbn(isbn)

@router.get("/outstandingloans", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_outstanding_loans(current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return find_outstanding()
    raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")