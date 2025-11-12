from pydantic import BaseModel, Field

class Rating(BaseModel):
    ratingid : str
    isbn : str
    rating : int 
    
class RatingCreate(BaseModel):
    isbn : str
    rating : int
    
class RatingUpdate(BaseModel):
    rating : int