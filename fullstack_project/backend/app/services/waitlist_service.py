import uuid
from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from app.schemas.waitlist import WaitList, WaitListCreate
from app.repositories.waitlists_repo import load_all, save_all

#Creates a waitlist for a user and a book
def create_waitlist(newWaitList: WaitListCreate) -> WaitList:
    waitlists = load_all()
    last_position = -1
    for waitlist in waitlists:
        if waitlist.get('isbn') != newWaitList.isbn:
            continue
        if waitlist.get('userid') == newWaitList.userid:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f"Waitlist for '{newWaitList.userid}' already exists")
        position_found = int(waitlist.get('position'))
        if position_found > last_position:
            last_position = position_found
            
    new_record = WaitList(isbn= newWaitList.isbn,
                          userid= newWaitList.userid,
                          position= last_position + 1)
    waitlists.append(new_record.model_dump())
    save_all(waitlists)
    return new_record

#Gets all the waitlist for a user
def get_waitlists_for_user(userid : str) -> List[WaitList]:
    waitlists = load_all()
    lists = []
    for waitlist in waitlists:
        if waitlist.get('userid') == userid:
            lists.append(WaitList(**waitlist))
    if len(lists) == 0:
        raise HTTPException(status_code=404, detail=f"No waitlists for '{userid}' not found")
    return lists

#Gets all the waitlists associated with a book
def get_waitlists_for_books(isbn : str) -> List[WaitList]:
    waitlists = load_all()
    lists = []
    for waitlist in waitlists:
        if waitlist.get('isbn') == isbn:
            lists.append(WaitList(**waitlist))
    if len(lists) == 0:
        raise HTTPException(status_code=404, detail=f"No waitlists for '{isbn}' not found")
    return lists

# Gets a Waitlist for a specific user and book
def get_specific_waitlist(userid : str, isbn : str) -> WaitList:
    waitlists = load_all()
    for waitlist in waitlists:
        if waitlist.get('userid') == userid and waitlist.get('isbn') == isbn:
            return WaitList(**waitlist)
    raise HTTPException(status_code=404, detail=f"No waitlists for user '{userid}' under book {isbn} found")

#Deletes all waitlists for a user
def delete_waitlists_for_user(userid : str) -> None:
    waitlists = load_all()
    new_waitlists = [waitlist for waitlist in waitlists if waitlist.get('userid') != userid]
    if len(new_waitlists) == len(waitlists):
        raise HTTPException(status_code=404, detail=f"Waitlists user {userid} not found")
    waitlists = new_waitlists
    save_all(waitlists)
    
#Deletes all waitlists for a book
def delete_waitlists_for_book(isbn : str) -> None:
    waitlists = load_all()
    new_waitlists = [waitlist for waitlist in waitlists if waitlist.get("isbn") != isbn]
    if len(new_waitlists) == len(waitlists):
        raise HTTPException(status_code=404, detail=f"Waitlists for book '{isbn}' not found")
    waitlists = new_waitlists
    save_all(waitlists)
    
#Deletes a waitlist for a user on a specific book
def delete_specific_waitlist(isbn : str, userid :str) -> None:
    waitlists = load_all()
    new_waitlists = [waitlist for waitlist in waitlists if not (waitlist.get("isbn") == isbn and waitlist.get('userid') == userid)]
    if len(new_waitlists) == len(waitlists):
        raise HTTPException(status_code=404, detail=f"Waitlist for book '{isbn}' and user {userid} not found")
    waitlists = new_waitlists
    save_all(waitlists)
    
#Deincrements all the positions in the waitlists by 1
def update_waitlists(isbn : str) -> None:
    waitlists = load_all()
    called_once = False
    for idx, waitlist in enumerate(waitlists):
        if waitlist.get('isbn') == isbn:
            updated_waitlist = WaitList(**waitlist)
            updated_waitlist.position-= 1
            waitlists[idx] = updated_waitlist.model_dump()
            called_once = True
    if not called_once:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No waitlists for book {isbn} found")
    save_all(waitlists)