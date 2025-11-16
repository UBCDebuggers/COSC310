import uuid
import bcrypt
from typing import List
from fastapi import HTTPException
from app.schemas.authentication import LoginRequest
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.users_repo import load_all, save_all
from app.core.security import bcrypt_context
from warnings import deprecated

#Returns a list of all users on the system
def list_users() -> List[User]:
    return [User(**attributes) for attributes in load_all()]

#Creates a new user
def create_user(newUser: UserCreate) -> User:
    users = load_all()
    newId = str(uuid.uuid4())
    while any(user.get("userid") == newId for user in users):
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

#Gets a users details using their userid
def get_user_by_id(user_id: str) -> User:
    users = load_all()
    for user in users:
        if user.get('userid') == user_id:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

#Gets a users details using their email
def get_user_by_email(email: str) -> User:
    users = load_all()
    for user in users:
        if user.get('email') == email:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"Email: '{email}' not found")

#Gets a users details using their username
@deprecated("Use get_user_by_email() or get_user_by_id() instead")
def get_user_by_username(username : str) -> User:
    users = load_all()
    for user in users:
        if user.get('username') == username:
            return User(**user)
    raise HTTPException(status_code=404, detail=f"User: '{username}' not found")

#Checks if entered cresidentials match
def authenticate_user(payload : LoginRequest) -> User:
    users = load_all()
    found = None
    for user in users:
        if user.get('email') == payload.username_email or user.get('username') == payload.username_email:
            found = user
            break
    
    if found:
        stored_password_str = str(user.get("hash_password"))
        
        stored_password_bytes = stored_password_str.encode('utf-8')
        password_bytes = payload.password.encode('utf-8')
        
        if bcrypt_context.verify(password_bytes, stored_password_bytes):
            return User(**found)
    return None
        
#Updates a users details
def update_user(user_id: str, userUpdate : UserUpdate) -> User:
    users = load_all()
    for userid, user in enumerate(users):
        if user.get("userid") == user_id:
            updated = User(userid = user_id,
                           email = userUpdate.email.strip(),
                           hash_password = userUpdate.password.strip(),
                           is_admin = userUpdate.is_admin.strip(),
                           department = userUpdate.department.strip(),
                           age = userUpdate.age,
                           username = userUpdate.username.strip(),
                           firstname = userUpdate.firstname.strip(),
                           lastname = userUpdate.lastname.strip()
                           )
            users[userid] = updated.model_dump()
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

#Deletes a users details
def delete_user(user_id: str) -> None:
    users = load_all()
    new_user = [user for user in users if user.get('userid') != user_id]
    if len(new_user) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_all(new_user)