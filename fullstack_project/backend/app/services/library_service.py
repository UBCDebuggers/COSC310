from datetime import datetime
from app.schemas.reservation import BookReservationCreate, NOT_RETURNED
from app.schemas.waitlist import WaitListCreate
from app.services.reservation_service import create_reservation
from app.services.waitlist_service import create_waitlist, get_waitlists_for_books, get_specific_waitlist, delete_specific_waitlist
from fastapi import HTTPException, status

def borrow_book(userid : str,  isbn : str, is_admin : bool, due_date : datetime):
    try:
        waitlist_entry = get_specific_waitlist(userid, isbn)
        position = waitlist_entry.position
        
        if position == 0:
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Please ask your librarian to complete this action for you."
                )
            create_reservation(BookReservationCreate(isbn=isbn, userid=userid, expiry_date=due_date, 
                status=NOT_RETURNED
            ))
            delete_specific_waitlist(isbn, userid)
            return {"message": "Book reserved from the top of the waitlist."}

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Please try again when you are at the top of the waitlist!"
            )
            
    except HTTPException as e:
        if e.status_code != status.HTTP_404_NOT_FOUND:
            raise e
            
    try:
        get_waitlists_for_books(isbn)
        create_waitlist(WaitListCreate(isbn=isbn, userid=userid))
        return {"message": "Book is unavailable. You have been added to the waitlist."}
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            create_reservation(BookReservationCreate(isbn=isbn, userid=userid, expiry_date=due_date))
            return {"message": "Book reserved successfully. Please visit a librarian as soon as possible get the book."}
        else:
            raise e