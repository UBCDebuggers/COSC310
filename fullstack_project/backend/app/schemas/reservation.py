from datetime import datetime, timedelta, timezone
import uuid
from pydantic import BaseModel, Field

NOT_RETURNED = 0
RETURNED = 1
RETURNED_OVERDUE = 2
NOT_RETURNED_OVERDUE = 3
CANCELLED = 4

class BookReservation(BaseModel):
    reservation_id : str = Field(default_factory= lambda: str(uuid.uuid4()))
    isbn : str
    userid : str
    reservation_date : datetime = Field(default_factory=datetime.now)
    status : int = RETURNED
    expiry_date : datetime = Field(default_factory=lambda:(datetime.now(timezone.utc) + timedelta(days=1)))
    active : bool = True
    
class BookReservationCreate(BaseModel):
    userid : str
    isbn : str
    status : int = RETURNED
    expiry_date : datetime = Field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(days=14)))
    active : bool = True