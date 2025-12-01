import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.security import verify_access_token
from app.schemas.penalties import Penalty, PenaltyCreate
from app.schemas.reservation import BookReservationCreate, BookReservation, RETURNED, NOT_RETURNED, RETURNED_OVERDUE, NOT_RETURNED_OVERDUE, CANCELLED
from app.services.library_service import borrow_book, return_book
from app.services.penalties_service import create_penalty, deactivate_penalty, delete_penalties_for_user, delete_penalty, get_penalties, get_penalties_for_user, get_penalty, reactivate_penalty, update_penalty
from app.services.reservation_service import get_reservations_by_userid, update_reservation, get_latest_reservation_by_isbn, get_reservations_by_isbn, find_outstanding

router = APIRouter(prefix="/library", tags=["library"], dependencies= [Depends(verify_access_token)])

#allows for a user to borrow a book and admin to accept a reservation
@router.post("/borrow", status_code= status.HTTP_200_OK, response_model=dict)
async def borrow(reservation_id : str, payload : BookReservationCreate, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return update_reservation(reservation_id, payload)
    else:
        return borrow_book(userid= current_user.get('userid'), isbn= payload.isbn, due_date= payload.expiry_date, is_admin= False)
    
#allows for an admin to confirm a book return
@router.put("/return", status_code= status.HTTP_200_OK, response_model=dict)
async def book_return(userid : str, isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return return_book(userid, isbn)

#gets all loans for the logged in user
@router.get("/userloans", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_user_loans(userid : str, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return get_reservations_by_userid(userid)
    return get_reservations_by_userid(current_user.get('userid'))

#gets latest reservation for a book
@router.get("/bookstatus/{isbn}", status_code= status.HTTP_200_OK, response_model=dict)
async def get_book_status(isbn : str):
    reservation = get_latest_reservation_by_isbn(isbn)
    if reservation.status in [RETURNED, RETURNED_OVERDUE, CANCELLED] or not reservation.active:
        return {"status" : "available"}
    elif reservation.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE]:
        return {"status" : "unavailable"}
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

#gets a books reservation history
@router.get("/bookhistory/{isbn}", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_book_history(isbn : str):
    return get_reservations_by_isbn(isbn)

#gets all outstanding loans
@router.get("/outstandingloans", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_outstanding_loans(current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return find_outstanding()
    raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")

#creates user restrictions
@router.post("/createpenalty", status_code= status.HTTP_201_CREATED, response_model= Penalty)
async def penalise_user(payload : PenaltyCreate, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return create_penalty(payload)

#gets user restrictions
@router.get("/penaltyof/{userid}", status_code= status.HTTP_200_OK, response_model=List[Penalty])
async def get_user_penalties(userid : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return get_penalties_for_user(userid)

#gets all active user restrictions
@router.get("/activepenalties", status_code= status.HTTP_200_OK, response_model=List[Penalty])
async def get_active_penalties(userid : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return get_penalties()

#gets user restrictions by restriction id
@router.get("/penalty/{penalty_id}", status_code= status.HTTP_200_OK, response_model=Penalty)
async def get_penalty_by_id(penalty_id : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return get_penalty(penalty_id)

#deletes user resitrictions by restriction id
@router.delete("/delete/{penalty}", status_code= status.HTTP_200_OK)
async def delete_penalty_by_id(penalty_id : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return delete_penalty(penalty_id)

#deletes user restrictions for a user
@router.delete("/deleteof/{userid}", status_code= status.HTTP_200_OK)
async def delete_user_penalties(userid : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return delete_penalties_for_user(userid)

#deactivates restrictions
@router.put("/deactivate/{penalty_id}", status_code= status.HTTP_200_OK, response_model=Penalty)
async def deactivate_restrictions(penalty_id : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return deactivate_penalty(penalty_id)

#re-enforces restrictions
@router.put("/reactivate/{penalty_id}", status_code= status.HTTP_200_OK, response_model=Penalty)
async def reactivate_restrictions(penalty_id : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return reactivate_penalty(penalty_id)

#updates restrictions
@router.put("/updatepenalty/{penalty_id}", status_code= status.HTTP_200_OK, response_model=Penalty)
async def update_restrictions(penalty_id : str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return update_penalty(penalty_id)
