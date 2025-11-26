from datetime import datetime, timedelta, timezone
import uuid
from pydantic import BaseModel, Field

TEMPORARY_BAN = 0
DEACTIVATED = 1
LIMITED_ACTIONS = 2
PERMANENT_BAN = 3

class Pentalty(BaseModel):
    penalty_id : str = Field(default_factory= lambda: str(uuid.uuid4()))
    userid : str
    penalty_type : int = TEMPORARY_BAN
    description : str = "Visit your librarian for more information"
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    expiry_date : datetime = Field(default_factory= lambda: datetime.now(timezone.utc) + timedelta(days=1))
    active : bool
    
class PenaltyCreate(BaseModel):
    userid : str
    penalty_type : int = TEMPORARY_BAN
    description : str = "Visit your librarian for more information"
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    expiry_date : datetime = Field(default_factory= lambda: datetime.now(timezone.utc) + timedelta(days=1))
    
class PenaltyUpdate(BaseModel):
    penalty_type : int = TEMPORARY_BAN
    description : str = "Visit your librarian for more information"
    timestamp : datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    expiry_date : datetime = Field(default_factory= lambda: datetime.now(timezone.utc) + timedelta(days=1))
    active : bool