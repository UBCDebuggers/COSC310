from pydantic import BaseModel, Field

class Rating(BaseModel):
    id : str
    isbn : str
    rating : int = Field(min_length=1, max_length=5)
    
class RatingCreate(BaseModel):
    id : str
    isbn : str
    rating : str
    
class RatingUpdate(BaseModel):
    rating : str