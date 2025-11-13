from typing import List
from datetime import datetime
import uuid
from app.schemas.reservation import BookReservation, BookReservationCreate, CANCELLED, NOT_RETURNED, NOT_RETURNED_OVERDUE, RETURNED, RETURNED_OVERDUE
from app.repositories.reservations_repo import load_all, save_all
from fastapi import HTTPException,status

RESERVATIONS = load_all()

def get_reservations_by_isbn(isbn : str) -> List[BookReservation]:
    global RESERVATIONS
    found = []
    for reservation in RESERVATIONS:
        if reservation.get('isbn') == isbn:
            found.append(BookReservation(**reservation))
    if found:
        return found
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for book {isbn}")

def get_reservations_by_userid(userid : str) -> List[BookReservation]:
    global RESERVATIONS
    found = []
    for reservation in RESERVATIONS:
        if reservation.get('userid') == userid:
            found.append(BookReservation(**reservation))
    if found:
        return found
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for user {userid}")

def get_latest_reservation_by_isbn(isbn : str) -> BookReservation:
    global RESERVATIONS
    curr_date = datetime.now()
    reservations_for_book = [reservation for reservation in RESERVATIONS if reservation.get('isbn') == isbn]
        
    closest = min(reservations_for_book, key=lambda r: abs(datetime.fromisoformat(r['reservation_date']) - curr_date)) if reservations_for_book else None
    if closest:
        return BookReservation(**closest)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for book {isbn}")

def get_latest_reservation_by_userid(userid : str) -> BookReservation:
    global RESERVATIONS
    curr_date = datetime.now()
    reservations_for_book = [reservation for reservation in RESERVATIONS if reservation.get('userid') == userid]
        
    closest = min(reservations_for_book, key=lambda r: abs(datetime.fromisoformat(r['reservation_date']) - curr_date)) if reservations_for_book else None
    if closest:
        return BookReservation(**closest)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for user {userid}")

def create_reservation(newReservation : BookReservationCreate) -> BookReservation:
    global RESERVATIONS
    try:
        book = get_latest_reservation_by_isbn(newReservation.isbn)
        if book.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Book {book.isbn} is currently outstanding or on loan")

        
    try:
        user = get_latest_reservation_by_userid(newReservation.userid)
        if user.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Please return any outstanding books before attempting to reserve a book for user {user.userid}")

    new_record = BookReservation(
                                 isbn= newReservation.isbn,
                                 userid= newReservation.userid,
                                 expiry_date= newReservation.expiry_date)
    
    RESERVATIONS.append(new_record.model_dump())
    
    save_all(RESERVATIONS)
    return new_record

    