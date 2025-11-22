from datetime import datetime, timezone
from typing import Union
from pydantic import BaseModel, Field

class Rating(BaseModel):
    userid : str
    isbn : str
    rating : int
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None
    
class RatingCreate(BaseModel):
    isbn : str
    rating : str
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None
    
class RatingUpdate(BaseModel):
    rating : str
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None