from typing import Optional
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    isbn: str
    score: int = Field(..., ge=0, le=10)


class RatingUpdate(BaseModel):
    score: int = Field(..., ge=0, le=10)


class RatedBook(BaseModel):
    user_id: str
    isbn: str
    title: Optional[str] = None
    author: Optional[str] = None
    year_of_publication: Optional[str] = None
    publisher: Optional[str] = None
    img_url_s: Optional[str] = None
    img_url_m: Optional[str] = None
    img_url_l: Optional[str] = None
    score: int
    created_on: str
