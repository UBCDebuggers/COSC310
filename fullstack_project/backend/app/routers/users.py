from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import verify_access_token
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.users_service import get_user_by_id, list_users, create_user, delete_user, update_user

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(verify_access_token)])

@router.get("", response_model=List[User])
def get_Users():
    return list_users()

#simple post the payload (is the body of the request)
@router.post("", response_model=User, status_code=201)
def post_user(payload: UserCreate, token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return create_user(payload)

@router.get("/{id}", response_model=User)
def get_user(id: str):
    return get_user_by_id(id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.post("", response_model=User, status_code=status.HTTP_200_OK)
def put_user(payload: UserUpdate, token_data : dict = Depends(verify_access_token)):
    return update_user(token_data['userid'], payload)

## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_admin(id: str, token_data : dict = Depends(verify_access_token)):
    if not token_data['is_admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    delete_user(id)
    return None

# removes a users profile permanently
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_admin(token_data : dict = Depends(verify_access_token)):
    delete_user(token_data['userid'])
    return None