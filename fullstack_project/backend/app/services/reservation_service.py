from typing import List
from datetime import datetime, timezone
from app.schemas.reservation import BookReservation, BookReservationCreate, CANCELLED, NOT_RETURNED, NOT_RETURNED_OVERDUE, RETURNED, RETURNED_OVERDUE
from app.repositories.reservations_repo import load_all, save_all
from fastapi import HTTPException,status

#Gets all historic reservations for a book
def get_reservations_by_isbn(isbn : str) -> List[BookReservation]:
    reservations = load_all()
    found = []
    for reservation in reservations:
        if reservation.get('isbn') == isbn:
            found.append(BookReservation(**reservation))
    if found:
        return found
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for book {isbn}")

#Gets all historic reservations for a user
def get_reservations_by_userid(userid : str) -> List[BookReservation]:
    reservations = load_all()
    found = []
    for reservation in reservations:
        if reservation.get('userid') == userid:
            found.append(BookReservation(**reservation))
    if found:
        return found
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for user {userid}")

#Gets the most recent book reservation for a given ISBN
def get_latest_reservation_by_isbn(isbn : str) -> BookReservation:
    reservations = load_all()
    curr_date = datetime.now()
    reservations_for_book = [reservation for reservation in reservations if reservation.get('isbn') == isbn]
        
    closest = min(reservations_for_book, key=lambda r: abs(datetime.fromisoformat(r['reservation_date']) - curr_date)) if reservations_for_book else None
    if closest:
        return BookReservation(**closest)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for book {isbn}")

#Gets the most recent book reservation for a given userid
def get_latest_reservation_by_userid(userid : str) -> BookReservation:
    reservations = load_all()
    curr_date = datetime.now()
    reservations_for_book = [reservation for reservation in reservations if reservation.get('userid') == userid]
        
    closest = min(reservations_for_book, key=lambda r: abs(datetime.fromisoformat(r['reservation_date']) - curr_date)) if reservations_for_book else None
    if closest:
        return BookReservation(**closest)
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Could not find any reservations for user {userid}")

#Creates a reservation if book is available and user has no outstanding loans
def create_reservation(newReservation : BookReservationCreate) -> BookReservation:
    reservations = load_all()
    now = datetime.now(timezone.utc)
    try:
        book = get_latest_reservation_by_isbn(newReservation.isbn)
        if book.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE] or book.expiry_date < now:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Book {book.isbn} is currently outstanding or on loan")

        
    try:
        user = get_latest_reservation_by_userid(newReservation.userid)
        if user.status in [NOT_RETURNED, NOT_RETURNED_OVERDUE] or user.expiry_date < now:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Please return any outstanding books before attempting to reserve a book for user {user.userid}")

    new_record = BookReservation(isbn= newReservation.isbn,
                                 userid= newReservation.userid,
                                 expiry_date= newReservation.expiry_date)
    
    reservations.append(new_record.model_dump())
    save_all(reservations)
    return new_record

#Updates a book reservation
def update_reservation(reservation_id : str, update : BookReservationCreate) -> BookReservation:
    reservations = load_all()
    for idx, reservation in enumerate(reservations):
        if reservation.get('reservation_id') == reservation_id:
            updated_reservation = BookReservation(isbn= update.isbn,
                                                  userid= update.userid,
                                                  reservation_date= reservation.get('reservation_date'),
                                                  expiry_date= update.expiry_date,
                                                  status= update.status,
                                                  reservation_id= reservation.get('reservation_id')
                                                  )
            reservations[idx] = updated_reservation.model_dump()
            save_all(reservations)
            return updated_reservation
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Reservation {reservation_id} not found")

#Deletes a book reservation
def delete_reservation(reservation_id : str) -> None:
    reservations = load_all()
    new_reservations = []
    for reservation in reservations:
        if reservation.get('reservation_id') == reservation_id:
            continue
        new_reservations.append(reservation)
    if len(new_reservations) == len(reservations):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Reservation {reservation_id} not found")
    reservations = new_reservations
    save_all(reservations)
    return None

#Deletes all reservations for a given book returns how many were deleted
def delete_reservations_for_book(isbn : str) -> int:
    reservations = load_all()
    new_reservations = []
    for reservation in reservations:
        if reservation.get('isbn') == isbn:
            continue
        new_reservations.append(reservation)
    difference = len(reservations) - len(new_reservations)
    if difference == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No reservations for book {isbn} found")
    reservations = new_reservations
    save_all(reservations)
    return difference

#Deletes all reservations for a given user returns how many were deleted
def delete_reservations_for_user(userid : str) -> int:
    reservations = load_all()
    new_reservations = []
    for reservation in reservations:
        if reservation.get('userid') == userid:
            continue
        new_reservations.append(reservation)
    difference = len(reservations) - len(new_reservations)
    if difference == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No reservations for user {userid} found")
    reservations = new_reservations
    save_all(reservations)
    return difference