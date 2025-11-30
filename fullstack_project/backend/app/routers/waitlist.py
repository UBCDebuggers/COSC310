from app.schemas.waitlist import WaitList
from app.services.waitlist_service import (get_waitlists_for_books, get_waitlists_for_user, 
                                           get_specific_waitlist, delete_specific_waitlist,
                                           delete_waitlists_for_user, delete_waitlists_for_book)
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token

router = APIRouter(prefix= "/waitlists", tags= ["waitlists"])

@router.get("/book/{isbn}", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary="Gets all existing waitlists for a book")
async def get_book_waitlists(isbn : str):
    return get_waitlists_for_books(isbn)

@router.get("/user", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Gets all existing waitlists for a user")
async def get_user_waitlists(current_user : dict = Depends(verify_access_token)):
    return get_waitlists_for_user(current_user.get('userid'))

@router.get("/{isbn}", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Gets a waitlist for the logged in user on a specific book")
async def get_waitlist(isbn :str, current_user : dict = Depends(verify_access_token)):
    return get_specific_waitlist(current_user.get('userid'), isbn)

@router.delete("/delete/{isbn}", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Deletes a waitlist for a specific book for a user")
async def delete_waitlist(isbn :str, current_user : dict = Depends(verify_access_token)):
    return delete_specific_waitlist(userid= current_user.get('userid'), isbn=isbn)

@router.delete("/user/delete", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Deletes all waitlists for a user")
async def delete_all_waitlists(current_user : dict = Depends(verify_access_token)):
    return delete_waitlists_for_user(current_user.get('userid'))

@router.delete("/books/delete/{isbn}", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Deletes all waitlists for a book")
async def delete_all_waitlists(isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You are not authorized to complete this action")
    return delete_waitlists_for_user(isbn)

@router.delete("/users/admin/delete/", status_code= status.HTTP_200_OK, response_model= List[WaitList], summary= "Deletes all waitlists for a book")
async def delete_all_waitlists(userid :str, isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You are not authorized to complete this action")
    return delete_specific_waitlist(isbn, userid)
