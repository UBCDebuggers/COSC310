from datetime import datetime, timezone
from typing import Optional, Union
from pydantic import BaseModel, Field

class Rating(BaseModel):
    userid : str
    isbn : str
    rating : int
    timestamp : Optional[datetime] = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None
    
class RatingCreate(BaseModel):
    isbn : str
    rating : int
    timestamp : Optional[datetime] = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None
    
class RatingUpdate(BaseModel):
    rating : int
    timestamp : Optional[datetime] = Field(default_factory= lambda: datetime.now(timezone.utc))
    description : Union[str, None] = None