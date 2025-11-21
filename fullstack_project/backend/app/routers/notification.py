from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from app.schemas.notification import Notification
from app.repositories import users_repo
from app.services import notification_service
from app.services.email_service import send_notification_email

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Get all notifications for a user.
@router.get("/{userid}")
def get_user_notifications(userid: str) -> List[dict]:
    try:
        notifications = notification_service.get_notifications_by_userid(userid)
        if not notifications:
            return []
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

# Get unread notifications for a user.
@router.get("/{userid}/unread")
def get_unread_notifications(userid: str) -> dict:
    try:
        notifications = notification_service.get_notifications_by_userid(userid)
        unread = [n for n in notifications if not n.get("isread")]

        return {
            "notifications": [Notification(**notif) for notif in unread],
            "count": len(unread)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching unread notifications: {str(e)}")

# Create a notification and optionally send an email to the user.
@router.post("/create")
def create_notification_with_email(
    background_tasks: BackgroundTasks,
    userid: str,
    notification_type: str,
    category: str,
    message: str,
    relatedid: str,
    send_email: bool = True
) -> dict:
    try:
        user = users_repo.get_user(userid)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{userid}' not found")
        
        notification = notification_service.add_notification(
            userid=userid,
            notification_type=notification_type,
            category=category,
            message=message,
            relatedid=relatedid
        )

        if send_email and user.get("email"):
            background_tasks.add_task(
                send_notification_email,
                to_email=user["email"],
                notification_type=notification_type,
                category=category,
                message=message
            )

        return {
            "status": "success",
            "message": "Notification created" + (" and email queued" if send_email else ""),
            "notification": Notification(**notification)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")

# Mark a notification as read
@router.put("/{notificationid}/read")
def mark_notification_as_read(notificationid: str) -> dict:
    try:
        updated = notification_service.update_notification(
            notificationid,
            {"isread": "true"}
        )

        if not updated:
            raise HTTPException(status_code=404, detail=f"Notification '{notificationid}' not found")

        return {
            "status": "success",
            "message": "Notification marked as read",
            "notification": Notification(**updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")