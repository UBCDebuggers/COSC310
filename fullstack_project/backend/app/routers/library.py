from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_access_token
from app.schemas.reservation import BookReservationCreate
from app.services.library_service import borrow_book, return_book

router = APIRouter(prefix="/library", tags=["library"])

@router.post("/borrow", status_code= status.HTTP_200_OK, response_model=dict)
async def borrow(payload : BookReservationCreate, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return borrow_book(userid= payload.userid, isbn= payload.isbn, due_date= payload.expiry_date, is_admin= True)
    else:
        return borrow_book(userid= current_user.get('sub'), isbn= payload.isbn, due_date= payload.expiry_date, is_admin= False)
    
@router.put("/return", status_code= status.HTTP_200_OK, response_model=dict)
async def book_return(userid : str, isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return return_book(userid, isbn)