from datetime import datetime, timezone
from app.schemas.reservation import RETURNED, RETURNED_OVERDUE, BookReservationCreate, NOT_RETURNED
from app.schemas.penalties import LIMITED_ACTIONS
from app.schemas.waitlist import WaitListCreate
from app.services.reservation_service import create_reservation, update_reservation, get_latest_reservation_by_isbn
from app.services.waitlist_service import create_waitlist, get_waitlists_for_books, get_specific_waitlist, delete_specific_waitlist
from app.services.penalties_service import get_penalties_for_user
from fastapi import HTTPException, status

def borrow_book(userid : str,  isbn : str, is_admin : bool, due_date : datetime) -> dict:
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
    
    check_restrictions(userid, "You are restricted from being added to waitlists.")
    try:
        get_waitlists_for_books(isbn)
        create_waitlist(WaitListCreate(isbn=isbn, userid=userid))
        return {"message": "Book is unavailable. You have been added to the waitlist."}
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            try:
                create_reservation(BookReservationCreate(isbn=isbn, userid=userid, expiry_date=due_date))
                return {"message": "Book reserved successfully. Please visit a librarian as soon as possible finish the transaction."}
            except HTTPException as e:
                if e.status_code == status.HTTP_403_FORBIDDEN:
                    create_waitlist(WaitListCreate(isbn=isbn, userid=userid))
                    return {"message": "Book is unavailable. You have been added to the waitlist."}
                raise e
        raise e
        
def return_book(userid : str, isbn : str) -> dict:
    reservation = get_latest_reservation_by_isbn(isbn)
    if reservation.userid != userid:
        raise HTTPException(status_code= status.HTTP_406_NOT_ACCEPTABLE, detail= f"User {userid} has not reserved book {isbn}")
    is_overdue = reservation.expiry_date < datetime.now(timezone.utc)
    new_record = BookReservationCreate(isbn= reservation.isbn,
                                        userid= reservation.userid,
                                        expiry_date= reservation.expiry_date,
                                        status= RETURNED_OVERDUE if is_overdue else RETURNED,
                                        active= False)
    update_reservation(reservation.reservation_id, new_record)
    return {"message": "Book successfully returned!"}

def check_restrictions(user_id : str, error : str) -> None:
    past_restrictions = None
    try:
        past_restrictions = get_penalties_for_user(user_id)
    except HTTPException:
        pass
    restrictions =  min(past_restrictions, key=lambda r: abs(r.timestamp - datetime.now(timezone.utc))) if past_restrictions else None
    if not restrictions:
        return None
    if restrictions.active and restrictions.penalty_type == LIMITED_ACTIONS:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= error)
    return None