from pydantic import BaseModel, Field
from datetime import datetime

class WaitList(BaseModel):    
    isbn : str
    userid : str
    timestamp : datetime = Field(default_factory=datetime.now)
    position : int
    
class WaitListCreate(BaseModel):
    isbn : str
    userid : str