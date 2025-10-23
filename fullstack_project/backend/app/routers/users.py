from fastapi import APIRouter, status
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.users_service import get_user_by_id, list_users, create_user, delete_user, update_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[User])
def get_Users():
    return list_users()

#simple post the payload (is the body of the request)
@router.post("", response_model=User, status_code=201)
def post_user(payload: UserCreate):
    return create_user(payload)

@router.get("/{id}", response_model=User)
def get_user(id: str):
    return get_user_by_id(id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{id}", response_model=User)
def put_user(id: str, payload: UserUpdate):
    return update_user(id, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(id: str):
    delete_user(id)
    return None