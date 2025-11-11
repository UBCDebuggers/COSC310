import datetime
from pydantic import BaseModel, ConfigDict, SkipValidation
from typing import Optional

class Request(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    requestid : str
    userid : str
    timestamp : SkipValidation[datetime]
    request_type : str
    details : str
    error_code : Optional[int] = None
    
class RequestCreate(BaseModel):
    userid : str
    request_type : str
    details : str
    error_code : Optional[int] = None