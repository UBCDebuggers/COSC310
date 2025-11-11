from pydantic import BaseModel

class DateRange(BaseModel):
    min : int | None
    max : int | None

class Filter(BaseModel):
    author : str | None
    publisher : str | None
    publish_date_range : DateRange | None