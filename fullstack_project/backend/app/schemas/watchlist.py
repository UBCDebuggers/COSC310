from pydantic import BaseModel
from typing import Optional

class WatchlistAdd(BaseModel):
    isbn: str

class WatchlistItem(BaseModel):
    isbn: str
    title: str
    author: Optional[str] = None
    year_of_publication: Optional[str] = None
    publisher: Optional[str] = None
    img_url_s: Optional[str] = None
    img_url_m: Optional[str] = None
    img_url_l: Optional[str] = None