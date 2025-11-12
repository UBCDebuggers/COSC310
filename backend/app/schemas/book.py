from pydantic import BaseModel

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
    isbn : str
    title : str
    author : str
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