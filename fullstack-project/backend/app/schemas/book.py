from pydantic import BaseModel

class Book(BaseModel):
    isbn : str
    title : str
    author : str
    year_of_publication : int
    publisher : str
    img_url_s : str
    img_url_m : str
    mg_url_l : str
    
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
    
    def csv_row_to_book(row: dict) -> Book:
        return Book(
            isbn = row["ISBN"],
            title = row["Book-Title"],
            author = row["Book-Author"],
            year_of_publication  = row["Year-Of-Publication"],
            publisher = row["Publisher"],
            img_url_s = row["Image-URL-S"],
            img_url_m = row["Image-URL-M"],
            img_url_l = row["Image-URL-L"]
        )