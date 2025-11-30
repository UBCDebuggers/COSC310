from pydantic import BaseModel, Field
from datetime import datetime

class Notification(BaseModel):
    userid: str
    notificationid: str
    type: str
    message: str
    timestamp: datetime
    isread: bool
    relatedid: str
    category: str

class NotificationCreate(BaseModel):
    type: str
    message: str
    timestamp: datetime
    isread: bool
    category: str
