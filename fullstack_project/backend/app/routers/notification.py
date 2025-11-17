from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from app.schemas.notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate,
)
from app.repositories import notification_repo, users_repo
from app.services.email_service import send_notification_email

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Get all notifications for a user.
@router.get("/{userid}")
def get_user_notifications(userid: str) -> List[dict]:
    try:
        notifications = notification_repo.get_notifications_by_userid(userid)
        if not notifications:
            return []
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

# Get unread notifications for a user.
@router.get("/{userid}/unread")
def get_unread_notifications(userid: str) -> dict:
    try:
        notifications = notification_repo.get_notifications_by_userid(userid)
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
        # Validate user exists
        user = users_repo.get_user(userid)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{userid}' not found")
        
        # Create notification record
        notification = notification_repo.add_notification(
            userid=userid,
            notification_type=notification_type,
            category=category,
            message=message,
            relatedid=relatedid
        )
        
        # Queue email in background if enabled
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
        updated = notification_repo.update_notification(
            notificationid,
            {"isread": "true"}  # CSV uses string "true"/"false"
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

# Update a notification.
@router.put("/{notificationid}")
def update_notification(notificationid: str, notification_update: NotificationUpdate) -> dict:
    try:
        updated = notification_repo.update_notification(
            notificationid,
            notification_update.model_dump()
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"Notification '{notificationid}' not found")
        
        return {
            "status": "success",
            "message": "Notification updated",
            "notification": Notification(**updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")

# Delete a notification
@router.delete("/{notificationid}")
def delete_notification(notificationid: str) -> dict:
    try:
        deleted = notification_repo.delete_notification(notificationid)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Notification '{notificationid}' not found")
        
        return {
            "status": "success",
            "message": "Notification deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

# Delete all read notifications for a user
@router.delete("/{userid}/read")
def delete_all_read_notifications(userid: str) -> dict:
    try:
        count = notification_repo.delete_read_notifications(userid)
        
        return {
            "status": "success",
            "message": f"Deleted {count} read notifications",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notifications: {str(e)}")
