from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id : str
    location : str
    age : str
    
class UserCreate(BaseModel):
    location : str
    age : str
    
class UserUpdate(BaseModel):
    location : str
    age : str