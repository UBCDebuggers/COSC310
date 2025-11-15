import uuid
from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from app.schemas.waitlist import WaitList, WaitListCreate
from app.repositories.waitlists_repo import load_all, save_all
    
WAITLISTS = load_all()

def create_waitlist(newWaitList: WaitListCreate) -> WaitList:
    global WAITLISTS
    last_position = -1
    for waitlist in WAITLISTS:
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
    WAITLISTS.append(new_record.model_dump())
    save_all(WAITLISTS)
    return new_record

def get_waitlists_for_user(userid : str) -> List[WaitList]:
    global WAITLISTS
    lists = []
    for waitlist in WAITLISTS:
        if waitlist.get('userid') == userid:
            lists.append(WaitList(**waitlist))
    if len(lists) == 0:
        raise HTTPException(status_code=404, detail=f"No waitlists for user '{userid}' found")
    return lists

def get_waitlists_for_books(isbn : str) -> List[WaitList]:
    global WAITLISTS
    lists = []
    for waitlist in WAITLISTS:
        if waitlist.get('isbn') == isbn:
            lists.append(WaitList(**waitlist))
    if len(lists) == 0:
        raise HTTPException(status_code=404, detail=f"No waitlists for book '{isbn}' found")
    return lists

def delete_waitlists_for_user(userid : str) -> None:
    global WAITLISTS
    new_waitlists = [waitlist for waitlist in WAITLISTS if waitlist.get('userid') != userid]
    if len(new_waitlists) == len(WAITLISTS):
        raise HTTPException(status_code=404, detail=f"Waitlists for user {userid} not found")
    WAITLISTS = new_waitlists
    save_all(WAITLISTS)
    
def delete_waitlists_for_book(isbn : str) -> None:
    global WAITLISTS
    new_waitlists = [waitlist for waitlist in WAITLISTS if waitlist.get("isbn") != isbn]
    if len(new_waitlists) == len(WAITLISTS):
        raise HTTPException(status_code=404, detail=f"Waitlists for book '{isbn}' not found")
    WAITLISTS = new_waitlists
    save_all(WAITLISTS)
    
def delete_specific_waitlist(isbn : str, userid :str) -> None:
    global WAITLISTS
    new_waitlists = [waitlist for waitlist in WAITLISTS if not (waitlist.get("isbn") == isbn and waitlist.get('userid') == userid)]
    if len(new_waitlists) == len(WAITLISTS):
        raise HTTPException(status_code=404, detail=f"Waitlist for book '{isbn}' and user {userid} not found")
    WAITLISTS = new_waitlists
    save_all(WAITLISTS)