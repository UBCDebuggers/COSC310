from typing import Optional
import uuid
from pydantic import BaseModel, Field

class User(BaseModel):
    userid : str = Field(default_factory= lambda: str(uuid.uuid4()))
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