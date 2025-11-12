from pydantic import BaseModel, Field

class Book(BaseModel):
    isbn : str
    title : str
    author : str
    year_of_publication : int
    publisher : str
    img_url_s : str
    img_url_m : str
    img_url_l : str
    
class BookCreate(BaseModel): 
    isbn : str = Field(min_length=10)
    title : str = Field(min_length=1)
    author : str = Field(min_length=1)
    year_of_publication : int
    publisher : str
    img_url_s : str
    img_url_m : str
    img_url_l : str
    
class BookUpdate(BaseModel):
    isbn : str
    title : str
    author : str
    year_of_publication : int
    publisher : str
    img_url_s : str
    img_url_m : str
    img_url_l : str