from typing import List
from app.repositories.penalties_repo import load_all, save_all
from app.schemas.penalties import PenaltyCreate, PenaltyUpdate, Penalty, PERMANENT_BAN
from fastapi import HTTPException, status

#Creates a user penalty
def create_penalty(penalty : PenaltyCreate) -> Penalty:
    penalties = load_all()
    filtered_penalties = [user_penalty for user_penalty in penalties 
                          if user_penalty.get('userid') == penalty.userid]
    if any(user_penalties.get('penalty_type') == PERMANENT_BAN for user_penalties in filtered_penalties):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= f"User {penalty.userid} has already been banned from the system.")
    
    new_record = Penalty(userid= penalty.userid,
                         penalty_type= penalty.penalty_type,
                         description= penalty.description,
                         timestamp= penalty.timestamp,
                         expiry_date= penalty.expiry_date
                         )
    penalties.append(new_record.model_dump())
    save_all(penalties)

#gets all penalties for a given user
def get_penalties_for_user(userid : str) -> List[Penalty]:
    penalties = load_all()
    found = []
    for penalty in penalties:
        if penalty.get('userid') == userid:
            found.append(Penalty(**penalty))
    if len(found) == 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"No penalties for user {userid} found")
    return found

#gets penalty using a penalty_id
def get_penalty(penalty_id : str) -> Penalty:
    penalties = load_all()
    found = None
    for penalty in penalties:
        if penalty.get('penalty_id') == penalty_id:
            found = Penalty(**penalty)
    if not found:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"No penalty {penalty_id} found")
    return found

#gets all active penalties on the system
def get_penalties() -> List[Penalty]:
    penalties = load_all()
    out = [Penalty(**penalty) for penalty in penalties]
    if len(out) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No penalties found")
    return out

#deletes a penalty
def delete_penalty(penalty_id: str) -> None:
    penalties = load_all()
    new_penalties = [penalty for penalty in penalties if penalty.get("penalty_id") != penalty_id]
    if len(new_penalties) == len(penalties):
        raise HTTPException(status_code=404, detail=f"Penalty '{penalty_id}' not found")
    save_all(new_penalties)
    
#deletes a penalties for a user
def delete_penalties_for_user(userid: str) -> None:
    penalties = load_all()
    new_penalties = [penalty for penalty in penalties if penalty.get("userid") != userid]
    if len(new_penalties) == len(penalties):
        raise HTTPException(status_code=404, detail=f"Penalties for user '{userid}' not found")
    save_all(new_penalties)
    
#updates a penalty
def update_penalty(penalty_id : str, update : PenaltyUpdate) -> Penalty:
    penalties = load_all()
    for idx, penalty in enumerate(penalties):
        if penalty.get('penalty_id') == penalty_id:
            new_record = Penalty(penalty_id= penalty.get('penalty_id'),
                         userid = penalty.get('userid'),
                         penalty_type= update.penalty_type,
                         description= update.description,
                         timestamp= update.timestamp,
                         expiry_date= update.expiry_date,
                         active= update.active)
            penalties[idx] = new_record.model_dump()
            save_all(penalties)
            return new_record
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Penalty {penalty_id} not found")

#Deactivate penalty
def deactivate_penalty(penalty_id : str) -> Penalty:
    penalties = load_all()
    for idx, penalty in enumerate(penalties):
        if penalty.get('penalty_id') == penalty_id:
            update = Penalty(**penalty)
            if not update.active:
                raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= f"Penalty {penalty_id} is not active")
            new_record = Penalty(penalty_id= update.penalty_id,
                         userid = update.userid,
                         penalty_type= update.penalty_type,
                         description= update.description,
                         timestamp= update.timestamp,
                         expiry_date= update.expiry_date,
                         active= False)
            penalties[idx] = new_record.model_dump()
            save_all(penalties)
            return new_record
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Penalty {penalty_id} not found")

#reactivates user
def reactivate_penalty(penalty_id : str) -> Penalty:
    penalties = load_all()
    for idx, penalty in enumerate(penalties):
        if penalty.get('penalty_id') == penalty_id:
            update = Penalty(**penalty)
            if update.active:
                raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= f"Penalty {penalty_id} is not active")
            new_record = Penalty(penalty_id= update.penalty_id,
                         userid = update.userid,
                         penalty_type= update.penalty_type,
                         description= update.description,
                         timestamp= update.timestamp,
                         expiry_date= update.expiry_date,
                         active= True)
            penalties[idx] = new_record.model_dump()
            save_all(penalties)
            return new_record
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Penalty {penalty_id} not found")