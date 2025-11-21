from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HistoryItem(BaseModel):
    userid: str
    isbn: str
    date: datetime

class HistoryItemCreate(BaseModel):
    userid: str
    isbn: str

class HistoryItemList(BaseModel):
    history_items : list[HistoryItem] = Field(default_factory=list)

class HistoryItemResponse(BaseModel):
    item: HistoryItem

class HistoryListResponse(BaseModel):
    items: list[HistoryItem] = Field(default_factory=list)

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None