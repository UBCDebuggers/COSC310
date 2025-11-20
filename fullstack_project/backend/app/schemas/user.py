from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    userid : str
    email : str
    hash_password : str
    is_admin : bool
    department : str
    age : int
    username : str
    firstname : str
    lastname : str
    
class UserCreate(BaseModel):
    email : str
    password : str
    is_admin : bool
    department : str
    age : int
    username : str
    firstname : str
    lastname : str
    
class UserUpdate(BaseModel):
    email : str
    password : str
    is_admin : bool
    department : str
    age : int
    username : str
    firstname : str
    lastname : str