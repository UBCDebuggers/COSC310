from pydantic import BaseModel

class Rating(BaseModel):
    id : str
    isbn : str
    rating : str
    
class RatingCreate(BaseModel):
    id : str
    isbn : str
    rating : str
    
class RatingUpdate(BaseModel):
    rating : str