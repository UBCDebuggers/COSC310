from pydantic import BaseModel

class Rating(BaseModel):
    id : int
    isbn : str
    rating : int
    
class RatingCreate(BaseModel):
    id : int
    isbn : str
    rating : int
    
class RatingUpdate(BaseModel):
    id : int
    isbn : str
    rating : int
    
    def csv_row_to_book(row: dict) -> Rating:
        return Rating(
            id = row["User-ID"],
            isbn = row["ISBN"],
            rating = row["Book-Rating"]
        )