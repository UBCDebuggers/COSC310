from pydantic import BaseModel

class User(BaseModel):
    id : int
    location : str
    age : int
    
class UserCreate(BaseModel):
    location : str
    age : int
    
class UserUpdate(BaseModel):
    location : str
    age : int
    
    def csv_row_to_book(row: dict) -> User:
        return User(
            id = row["User-ID"],
            location = row["Location"],
            age = row["Age"]
        )