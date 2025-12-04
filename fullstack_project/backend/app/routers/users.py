from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.users_service import get_user_by_id, list_users, create_user, delete_user, update_user

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(verify_access_token)])

#gets all users
@router.get("/getall", response_model=List[User])
def get_Users(token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return list_users()

#simple post the payload (is the body of the request)
@router.post("/create", response_model=User, status_code=201)
def post_user(payload: UserCreate, token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return create_user(payload)

#gets a user by userid , changed it so admins only can read user profiles.
@router.get("/get/{id}", response_model=User)
def get_user(id: str, token_data: dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return get_user_by_id(id)

#Updates a users profile
@router.put("/update", response_model=User, status_code=status.HTTP_200_OK)
def put_user(payload: UserUpdate, token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return update_user(token_data['userid'], payload)


#deletes a user using userid
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_admin(id: str, token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_user(id)
    return None

# removes a users profile permanently
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_admin(token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_user(token_data['userid'])
    return None
