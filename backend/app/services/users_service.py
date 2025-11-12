import uuid
import bcrypt
from typing import List
from fastapi import HTTPException
from app.schemas.authentication import LoginRequest
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.users_repo import load_all, save_all
from app.core.config import bcrypt_context

def list_users() -> List[User]:
    return [User(**attributes) for attributes in load_all()]

def create_user(newUser: UserCreate) -> User:
    users = load_all()
    newId = str(uuid.uuid4())
    while any(user.get("id") == newId for user in users):
        newId = str(uuid.uuid4())
    new_record = User(userid = newId,
                      email = newUser.email.strip(),
                      hash_password = bcrypt_context.hash(newUser.password.strip()),
                      is_admin = newUser.is_admin.strip(),
                      department = newUser.department.strip(),
                      age = newUser.age,
                      username = newUser.username.strip(),
                      firstname = newUser.firstname.strip(),
                      lastname = newUser.lastname.strip()
                      )
    users.append(new_record.model_dump())
    save_all(users)
    return new_record

def get_user_by_id(user_id: str) -> User:
    users = load_all()
    for user in users:
        if user.get('id') == user_id:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def get_user_by_email(email: str) -> User:
    users = load_all()
    for user in users:
        if user.get('eamil') == email:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"Email: '{email}' not found")

def get_user_by_username(username : str) -> User:
    users = load_all()
    for user in users:
        if user.get('username') == username:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"User: '{username}' not found")

def authenticate_user(payload : LoginRequest) -> User:
    users = load_all()
    found = None
    for user in users:
        if user.get('email') == payload.username_email or user.get('username') == payload.username_email:
            found = user
            break
    
    if found:
        #Get stored hashed password
        stored_password_str = str(user.get("hash_password"))
        
        #Convert stored hash password and entered password into bytes for safe comparing
        stored_password_bytes = stored_password_str.encode('utf-8')
        password_bytes = payload.password.encode('utf-8')
        
        #Safely compare with bcrypt
        if bcrypt_context.verify(password_bytes, stored_password_bytes):
            return User(**found)
    return None
        

def update_user(user_id: str, userUpdate : UserUpdate) -> User:
    users = load_all()
    for id, user in enumerate(users):
        if user.get("isbn") == user_id:
            updated = User(id = userUpdate,
                           email = userUpdate.email.strip(),
                           hash_password = userUpdate.password.strip(),
                           is_admin = userUpdate.is_admin.strip(),
                           department = userUpdate.department.strip(),
                           age = userUpdate.age,
                           username = userUpdate.username.strip(),
                           firstname = userUpdate.firstname.strip(),
                           lastname = userUpdate.lastname.strip()
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
        
            
    