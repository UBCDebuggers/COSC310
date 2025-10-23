from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id : str
    email : str
    hash_password : str
    is_admin : str
    department : str
    age : int
    
class UserCreate(BaseModel):
    email : str
    hash_password : str
    is_admin : str
    department : str
    age : int
    
class UserUpdate(BaseModel):
    email : str
    hash_password : str
    is_admin : str
    department : str
    age : int