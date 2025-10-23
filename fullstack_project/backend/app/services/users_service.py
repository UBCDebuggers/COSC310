import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.users_repo import load_all, save_all

def list_users() -> List[User]:
    return [User(**attributes) for attributes in load_all()]

def create_user(newUser: UserCreate) -> User:
    users = load_all()
    newId = str(uuid.uuid4())
    while any(user.get("id") == newId for user in users):
        newId = str(uuid.uuid4())
    new_record = User(id = newId,
                      email = newUser.email.strip(),
                      hash_password = newUser.hash_password.strip(),
                      is_admin = newUser.is_admin.strip(),
                      department = newUser.department.strip(),
                      age = newUser.age
                      )
    users.append(new_record.model_dump())
    save_all(users)
    return new_record

def get_user_by_id(user_id: str) -> User:
    users = load_all()
    for user in users:
        print("current user = ", user)
        if user.get('id') == user_id:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def update_user(user_id: str, userUpdate : UserUpdate) -> User:
    users = load_all()
    for id, user in enumerate(users):
        if user.get("isbn") == user_id:
            updated = User(id = userUpdate,
                           email = userUpdate.email.strip(),
                           hash_password = userUpdate.hash_password.strip(),
                           is_admin = userUpdate.is_admin.strip(),
                           department = userUpdate.department.strip(),
                           age = userUpdate.age
                           )
            users[id] = updated.model_dump()
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    users = load_all()
    new_user = [user for user in users if user.get('id') != user_id]
    if len(new_user) == len(users):
        HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_all(new_user)
        
            
    