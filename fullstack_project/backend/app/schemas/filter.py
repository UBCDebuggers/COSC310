from pydantic import BaseModel
from typing import Optional

class Filter(BaseModel):
    author : Optional[str] = None
    publisher : Optional[str] = None
    publish_date_min : Optional[int] = None
    publish_date_max : Optional[int] = None