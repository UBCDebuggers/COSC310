# How to send notifications to the app & email the user asynchronously
from fastapi import BackgroundTasks
from app.services.email_service import send_notification_email
from app.repositories import notification_repo

# Create a notification record and send email asynchronously
def create_notification_with_email(background_tasks: BackgroundTasks, userid: str, notification_type: str,
    category: str, message: str, relatedid: str, user_email: str) -> dict:
    
    notification = notification_repo.add_notification(
        userid=userid,
        notification_type=notification_type,
        category=category,
        message=message,
        relatedid=relatedid
    )
    
    background_tasks.add_task(
        send_notification_email,
        to_email=user_email,
        notification_type=notification_type,
        category=category,
        message=message
    )
    
    return notification