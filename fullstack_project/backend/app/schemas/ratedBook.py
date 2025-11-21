from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    isbn: str
    score: int = Field(..., ge=0, le=10)